from django.db import models

# Create your models here.
class Team(models.Model):
    name = models.CharField(max_length=100)
    coach = models.CharField(max_length=100)
    manager = models.CharField(max_length=100)

class TeamMember(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    # Add more fields for team members

class Venue(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)

class Fixture(models.Model):
    team_1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_1_fixtures')
    team_2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_2_fixtures')
    date_time = models.DateTimeField()
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)

class Result(models.Model):
    fixture = models.OneToOneField(Fixture, on_delete=models.CASCADE)
    goals_team_1 = models.PositiveIntegerField()
    goals_team_2 = models.PositiveIntegerField()