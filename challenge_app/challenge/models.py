from datetime import datetime, timezone

from django.contrib.auth import user_logged_in
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver


class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING, null=True)
    active_group = models.ForeignKey(Group, on_delete=models.DO_NOTHING, null=True)

    def current_score(self, group):
        try:
            return ScoreTransaction.objects.filter(player=self).filter(match__group=group).latest('match__played_at').score
        except:
            return 100

    def wins_from(self, player, match):
        s = player.current_score(group=match.group) * 0.25
        self.add_score(s, match)
        player.add_score(-s, match)

    def add_score(self, score, match):
        ScoreTransaction.objects.create(score=self.current_score(group=match.group) + score, player=self, match=match)

    @receiver(post_save, sender=User)
    def create_player(sender, instance, created, **kwargs):
        if created:
            Player.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_player(sender, instance, **kwargs):
        instance.player.save()

    @receiver(user_logged_in, sender=User)
    def set_active_group(sender, user, **kwargs):
        if (not user.player.active_group) & user.groups.exists():
            user.player.active_group = user.groups.last()

    def __str__(self):
        return self.user.username



class Match(models.Model):
    challenger = models.ForeignKey(Player, on_delete=models.DO_NOTHING, related_name='challenger')
    opponent = models.ForeignKey(Player, on_delete=models.DO_NOTHING, related_name='opponent')
    challenger_wins = models.BooleanField(null=True, blank=True)
    date = models.DateTimeField()
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    played_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    def submit_result(self, challenger_wins):
        if self.played_at:
            return
        self.challenger_wins = challenger_wins
        self.played_at = datetime.now(tz=timezone.utc)
        if challenger_wins:
            self.challenger.wins_from(self.opponent, self)
        else:
            self.opponent.wins_from(self.challenger, self)
        self.save()

    def __str__(self):
        return "{challenger} VS {opponent} ({date})".format(challenger=self.challenger.user.username,
                                                            opponent=self.opponent.user.username, date=self.date)


class ScoreTransaction(models.Model):
    # Last score will be its actual score. Earlier scores are stored for efficient statistics
    player = models.ForeignKey(Player, on_delete=models.DO_NOTHING)
    score = models.IntegerField(default=100)
    match = models.ForeignKey(Match, on_delete=models.CASCADE, null=True)

    # group = models.ForeignKey(Group, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.player.user.username}: {self.score} ({self.match.group})"


class JoinCode(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    key = models.TextField()
    expires_at = models.DateTimeField()
