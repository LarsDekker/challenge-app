from datetime import datetime, timezone

from django.contrib.auth.models import Group, User
from django.db.models import Q, Max
from django.test import TestCase

# Create your tests here.
from challenge.models import Match, Player, ScoreTransaction


class MatchSubmitTestase(TestCase):
    def setUp(self):
        # could probably be more efficient :)
        g = Group.objects.create(name="Testgroup")

        user1 = User.objects.create(username="person1")
        user2 = User.objects.create(username="person2")
        user3 = User.objects.create(username="person3")
        user4 = User.objects.create(username="person4")

        g.user_set.add(user1, user2)

        for u in [user1, user2, user3, user4]:
            u.player.active_group = g
            u.save()

        Match.objects.create(challenger=user1.player, opponent=user2.player, date=datetime.now(tz=timezone.utc), group=g)
        Match.objects.create(challenger=user3.player, opponent=user4.player, date=datetime.now(tz=timezone.utc), group=g)
        Match.objects.create(challenger=user3.player, opponent=user1.player, date=datetime.now(tz=timezone.utc), group=g)
        Match.objects.create(challenger=user2.player, opponent=user4.player, date=datetime.now(tz=timezone.utc), group=g)

    def test_players_can_submit(self):
        match = Match.objects.first()
        match.submit_result(challenger_wins=False)
        u = User.objects.get(username="person1")
        self.assertEqual(u.player.current_score(match.group), 75)

    def test_multiple_matches(self):
        matches = Match.objects.filter(played_at=None)

        for m in matches:
            m.submit_result(challenger_wins=True)

        u1 = User.objects.get(username="person1")
        u2 = User.objects.get(username="person2")
        u3 = User.objects.get(username="person3")
        u4 = User.objects.get(username="person4")

        g = u1.player.active_group

        print("Group {g}".format(g=g))

        self.assertEqual(93, u1.player.current_score(g))
        self.assertEqual(93, u2.player.current_score(g))
        self.assertEqual(156, u3.player.current_score(g))
        self.assertEqual(56, u4.player.current_score(g))
        print(ScoreTransaction.objects.all())
        self.assertEqual(2, ScoreTransaction.objects.filter(player=u1.player).count())

        # self.assertEqual()

