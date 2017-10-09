from database import Database
import operator

class WeekResult:
    def __init__(self, week, win, opponent_score, team_score, opponent):
        self.week=week
        self.win=win
        self.opponent_score=opponent_score
        self.team_score=team_score
        self.opponent=opponent

class YearResults:
    def __init__(self, year, wins, losses, week_results, team):
        self.year=year
        self.wins=wins
        self.losses=losses
        self.week_results=week_results
        self.team=team
    
def sortTeamHistory(team):
    years=[]
    temp_years=[]

    db = Database()
    years_played = db.getUserYears(team)
    #TODO: Find out why years_played come back as list of tuple of (year,)
    #Convert from list of tuples to list
    for year in years_played:
        temp_years.append(year[0])
    years_played = temp_years
    years_played.sort(reverse=True)
    for year in years_played:
        week_results=[]
        matchups = db.getUserMatchupsInYear(team,year)
        for matchup in matchups:
            if matchup.team_one == team:
                week = WeekResult(matchup.week,(matchup.team_one_score > matchup.team_two_score),matchup.team_two_score,matchup.team_one_score,matchup.team_two)
            else:
                week = WeekResult(matchup.week,(matchup.team_one_score > matchup.team_two_score),matchup.team_two_score,matchup.team_one_score,matchup.team_two)

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
