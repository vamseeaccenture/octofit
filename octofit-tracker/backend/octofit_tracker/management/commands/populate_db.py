from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from djongo import models

from octofit_tracker import settings

from django.db import connection

class Command(BaseCommand):
    help = 'Populate the octofit_db database with test data'

    def handle(self, *args, **options):
        User = get_user_model()
        # Delete all data
        User.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Deleted all users.'))

        # Create test users (superheroes)
        marvel_team = 'marvel'
        dc_team = 'dc'
        users = [
            User(username='ironman', email='ironman@marvel.com', first_name='Tony', last_name='Stark'),
            User(username='spiderman', email='spiderman@marvel.com', first_name='Peter', last_name='Parker'),
            User(username='batman', email='batman@dc.com', first_name='Bruce', last_name='Wayne'),
            User(username='superman', email='superman@dc.com', first_name='Clark', last_name='Kent'),
        ]
        for user in users:
            user.set_password('password123')
            user.save()
        self.stdout.write(self.style.SUCCESS('Created test users.'))

        # Create teams, activities, leaderboard, workouts collections using raw pymongo
        db = connection.cursor().db_conn
        db.teams.delete_many({})
        db.activities.delete_many({})
        db.leaderboard.delete_many({})
        db.workouts.delete_many({})

        db.teams.insert_many([
            {'name': marvel_team, 'members': ['ironman', 'spiderman']},
            {'name': dc_team, 'members': ['batman', 'superman']},
        ])
        db.activities.insert_many([
            {'user': 'ironman', 'activity': 'run', 'distance': 5},
            {'user': 'spiderman', 'activity': 'cycle', 'distance': 10},
            {'user': 'batman', 'activity': 'swim', 'distance': 2},
            {'user': 'superman', 'activity': 'fly', 'distance': 100},
        ])
        db.leaderboard.insert_many([
            {'team': marvel_team, 'points': 150},
            {'team': dc_team, 'points': 200},
        ])
        db.workouts.insert_many([
            {'name': 'Pushups', 'difficulty': 'easy'},
            {'name': 'Pullups', 'difficulty': 'medium'},
            {'name': 'Squats', 'difficulty': 'easy'},
        ])
        db.users.create_index('email', unique=True)
        self.stdout.write(self.style.SUCCESS('Created teams, activities, leaderboard, workouts, and unique index on users.email.'))
