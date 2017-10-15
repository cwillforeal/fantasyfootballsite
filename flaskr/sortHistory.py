from database import Database
import operator

class WeekResult:
    def __init__(self, week, win, opponent_score, team_score, opponent_key, opponent):
        self.week=week
        self.win=win
        self.opponent_score=opponent_score
        self.team_score=team_score
        self.opponent=opponent
        self.opponent_key=opponent_key

class YearResults:
    def __init__(self, year, wins, losses, week_results, user):
        self.year=year
        self.wins=wins
        self.losses=losses
        self.week_results=week_results
        self.user=user
    
class CareerResults:
    def __init__(self):
        self.user=None
        self.titles=[]
        self.reg_season_wins=0
        self.reg_season_loses=0
        self.playoff_wins=0
        self.playoff_loses=0
        self.points_for=0
        self.points_against=0
        self.seasons=0
        self.best_week=0
        self.worst_week=10000
        self.regular_season_titles=0

def sortTeamHistory(team,db):
    years=[]

    years_played = db.getUserYears(team)
    users = db.getUsers()
    #TODO: Find out why years_played come back as list of tuple of (year,)
    #Convert from list of tuples to list
    years_played.sort(reverse=True)
    for year in years_played:
        week_results=[]
        matchups = db.getUserMatchupsInYear(team,year)
        for matchup in matchups:
            if matchup.team_one == team:
                week = WeekResult(matchup.week,(matchup.team_one_score > matchup.team_two_score),matchup.team_two_score,matchup.team_one_score,matchup.team_two,db.getUser(matchup.team_two).name)
            else:
                week = WeekResult(matchup.week,(matchup.team_two_score > matchup.team_one_score),matchup.team_one_score,matchup.team_two_score,matchup.team_one,db.getUser(matchup.team_one).name)

            week_results.append(week)    

        week_results.sort(key=operator.attrgetter('week'))
        wins=0
        losses=0
        for week in week_results:
            if week.week >= 100:
                break
            if week.win == True:
                wins = wins + 1
            else:
                losses = losses + 1

        years.append(YearResults(year,wins,losses,week_results,team))
    
    return (years)

def getUserHistory(years_stats, user):
    career_results = CareerResults()
    career_results.user = user
    for year in years_stats:
        career_results.seasons = career_results.seasons + 1
        week_cnt = 0
        for week in year.week_results:
            week_cnt = week_cnt + 1 
            career_results.points_for = career_results.points_for +  week.team_score
            career_results.points_against = career_results.points_against + week.opponent_score
            if week.team_score > career_results.best_week:
                career_results.best_week = week.team_score
            if week.team_score < career_results.worst_week:
                career_results.worst_week = week.team_score 
            if week.week < 100:
                if week.win == True:
                    career_results.reg_season_wins = career_results.reg_season_wins + 1
                else:
                    career_results.reg_season_loses = career_results.reg_season_loses + 1
            elif week.week >= 100 and week.week < 200:
                if week.win == True:
                    career_results.playoff_wins = career_results.playoff_wins + 1
                    if week_cnt >= len(year.week_results):
                        career_results.titles.append(year.year)
                else:
                    career_results.playoff_loses = career_results.playoff_loses + 1

    return(career_results)
