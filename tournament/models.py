from django.db import models

class Venue(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Team(models.Model):
    name = models.CharField(max_length=100)
    coach = models.CharField(max_length=100)
    manager = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class TeamMember(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

class Match(models.Model):
    team1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team1_matches')
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team2_matches')
    date = models.DateField()
    venue = models.CharField(max_length=100)
    team1_goals = models.CharField(max_length=50)
    team2_goals = models.CharField(max_length=50)