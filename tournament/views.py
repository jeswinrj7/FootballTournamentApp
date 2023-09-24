from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q 
from django.contrib.auth.decorators import login_required
from .forms import TeamRegistrationForm, TeamMemberFormSet
from .models import Team, TeamMember, Match, Venue
from datetime import datetime, timedelta
import itertools, random

# Add a global variable to track whether the schedule has been generated
schedule_generated = False

def register_team(request):
    team_count = Team.objects.count()
    if team_count >= 10:
        # Registration is closed, redirect to an information page      
        return render(request, 'tournament/general_information.html', {'message': "Registration is closed."})

    if request.method == 'POST':
        form = TeamRegistrationForm(request.POST)
        member_formset = TeamMemberFormSet(request.POST)

        if form.is_valid() and member_formset.is_valid():
            # Create a Team instance and save it
            team = Team.objects.create(name=form.cleaned_data['name'], coach=form.cleaned_data['coach'], manager=form.cleaned_data['manager'])
            # Create TeamMember objects for each member
            for member_form in member_formset:
                member_name = member_form.cleaned_data.get('member_name')
                if member_name:
                    TeamMember.objects.create(team=team, name=member_name)
            
            team_count = Team.objects.count()
            if team_count >= 10:            
                return generate_schedule(request)
            else:
                return redirect('register')  # Redirect to a success page
    else:
        form = TeamRegistrationForm()
        member_formset = TeamMemberFormSet()

    return render(request, 'tournament/team_registration.html', {'form': form, 'member_formset': member_formset})

def index(request):
  return render(request, 'tournament/home.html')

def generate_schedule(request):
    # Retrieve all registered teams and venues
    match_count = Match.objects.count()
    team_count = Team.objects.count()
    if match_count > 0 and team_count >= 10 :
        matches = list(Match.objects.all())
        context = {
        'team_matches': matches,
        }
        return render(request, 'tournament/match_schedule.html', context)
    elif team_count < 10:
        # Registration is closed, redirect to an information page      
        return render(request, 'tournament/general_information.html', {'message': "Schedule page will be available after completing the registration."})
    else:
        teams = Team.objects.all()
        VENUE_NAMES = [
        "Venue A",
        "Venue B",
        "Venue C",
        "Venue D",
        "Venue E",
        ]

        for venue_name in VENUE_NAMES:
            Venue.objects.create(name=venue_name)
            
        venues = Venue.objects.all()

        # Shuffle the list of venues randomly
        shuffled_venues = list(venues)
        random.shuffle(shuffled_venues)

        # Create all possible combinations of teams
        teams_list = list(teams)
        team_combinations = list(itertools.combinations(teams_list, 2))
        random.shuffle(team_combinations)

        # Define the schedule parameters
        start_date = datetime(2023, 11, 4)  # Replace with your desired start date
        current_date = start_date
        matches = []

        # Create a dictionary to keep track of the last venue used for each team
        last_venue_used = {team: None for team in teams_list}

        for team1, team2 in team_combinations:
            # Try to find an available venue by reshuffling the list
            available_venues = [v for v in shuffled_venues if v != last_venue_used[team1] and v != last_venue_used[team2]]

            if not available_venues:
                # If no available venues are left, reshuffle the venues list
                shuffled_venues = list(venues)
                random.shuffle(shuffled_venues)
                available_venues = [v for v in shuffled_venues if v != last_venue_used[team1] and v != last_venue_used[team2]]

            venue = random.choice(available_venues)

            if venue:
                # Create the match
                match = Match.objects.create(
                    team1=team1,
                    team2=team2,
                    date=current_date,
                    venue=venue,
                    team1_goals='0',
                    team2_goals='0'
                )
                matches.append(match)

                # Update the last venue used for both teams
                last_venue_used[team1] = venue
                last_venue_used[team2] = venue

            # Move to the next day
            current_date += timedelta(days=1)

        context = {
            'team_matches': matches,
        }

        return render(request, 'tournament/match_schedule.html', context)

def team_information(request):
    match_count = Match.objects.count()
    team_count = Team.objects.count()
    if match_count < 0 or team_count < 10:
        return render(request, 'tournament/general_information.html', {'message': "Team Information page will be available after completing the registration."})
    else:
        teams = Team.objects.all()
        team_information = None  # Initialize team_information to None

        if request.method == 'POST':
            team_id = request.POST.get('team_select')
            if team_id:
                team = get_object_or_404(Team, pk=team_id)
                team_members = TeamMember.objects.filter(team=team)
                team_matches = Match.objects.filter(Q(team1=team) | Q(team2=team))
                
                # Create a dictionary with team information
                team_information = {
                    'team': team,
                    'manager': team.manager,
                    'coach': team.coach,
                    'members': team_members,
                    'matches': team_matches,
                }

        return render(request, 'tournament/team_information.html', {'teams': teams, 'team_information': team_information})

@login_required  # Only admin users can access this view
def update_goals(request):
    match_count = Match.objects.count()
    team_count = Team.objects.count()
    if match_count < 0 or team_count < 10:
        return render(request, 'tournament/general_information.html', {'message': "This page will be available after completing the registration."})
    else:
        teams = Team.objects.all()
        team1_id = request.POST.get('team1_select')
        team2_id = request.POST.get('team2_select')

        if team1_id and team2_id:
            team1 = get_object_or_404(Team, pk=team1_id)
            team2 = get_object_or_404(Team, pk=team2_id)

            if request.method == 'POST':
                if 'action' in request.POST and request.POST['action'] == 'Update Goals':
                    team1_goals = request.POST.get('team1_goals')
                    team2_goals = request.POST.get('team2_goals')  
                    matches = Match.objects.filter(team1=team1, team2=team2)
                    # Handle goal updates
                    for match in matches:                  
                        if team1_goals is not None and team2_goals is not None:
                            # Validate and update the goals                                                 
                            match.team1_goals = team1_goals
                            match.team2_goals = team2_goals                            
                            match.save()
                elif 'action' in request.POST and request.POST['action'] == 'Show Matches':
                    matches = Match.objects.filter(team1=team1, team2=team2)
                    if matches.exists():
                        return render(request, 'tournament/update_goals.html', {
                        'teams': teams,
                        'matches': matches if 'matches' in locals() else None,
                        'team1_id': int(team1_id),
                        'team2_id': int(team2_id),
                    })
                    else:
                        matches = Match.objects.filter(team1=team2, team2=team1)
                        temp = team1_id
                        team1_id = team2_id
                        team2_id = temp
                        return render(request, 'tournament/update_goals.html', {
                            'teams': teams,
                            'matches': matches if 'matches' in locals() else None,
                            'team1_id': int(team1_id),
                            'team2_id': int(team2_id),
                        })
            
        return render(request, 'tournament/update_goals.html', {
                'teams': teams,
                'matches': matches if 'matches' in locals() else None,
                'team1_id': team1_id,
                'team2_id': team2_id,
            })