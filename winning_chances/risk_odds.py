from random import randint
import itertools
import pandas as pd
import numpy as np
import inflect
from plotnine import *
import os

def get_dice_combs(n_of_dice,sides = 6):
  """"
  Returns all throw combinations of n dice with n sides.
  For each leaves two highest results sorted in descending order.
  E.g. for 3 dices and throw output [1,3,2] reurns [3,2].
  Returns dataframe, where n is the number of occurencies for each combination.
  """
  dice_out = list(range(1,sides+1))
  combs = []
  for element in itertools.product(dice_out,repeat = n_of_dice):
    comb = list(element)
    comb.sort(reverse = True)
    combs.append(comb)
  col_names = ['dice_' + str(dice_num) for dice_num in list(range(1,min(n_of_dice,2)+1))]
  combs = [c[0:min(n_of_dice,2)] for c in combs]
  df_combs = pd.DataFrame(combs,columns = col_names)
  df_combs['n'] = 1
  df_combs = df_combs.groupby(col_names,as_index = False).sum('n')
  return df_combs

def get_chances_from_combs(df_comb1,df_comb2):
  """
  Takes two dataframes created by get_dice_combs as arguments.
  Returns dataframe with:
    1. all possible combinations of outcomes for defender and attacker,
    2. number of possible occurencies for each combination,
    3. probability of getting each combiantion of outcome.
  Outcomes for defender and attacker are calculated based on "Risk" boardgame rules.
  Important: df_comb1 is always defender and df_comb2 is always attacker!!
  """
  df = df_comb1.merge(df_comb2,'cross')
  df['n'] = df.n_x * df.n_y
  df['result_1_def'] = np.where(df['dice_1_x']>=df['dice_1_y'],0,-1)
  df['result_1_att'] = np.where(df['dice_1_x']>=df['dice_1_y'],-1,0)
  if len(df_comb1.columns)>2 and len(df_comb2.columns)>2: 
    df['result_2_def'] = np.where(df['dice_2_x']>=df['dice_2_y'],0,-1)
    df['result_2_att'] = np.where(df['dice_2_x']>=df['dice_2_y'],-1,0)
    df['result_defender'] = df.result_1_def + df.result_2_def
    df['result_attacker'] = df.result_1_att + df.result_2_att
  else:
    df['result_defender'] = df.result_1_def
    df['result_attacker'] = df.result_1_att
  df_result = df.groupby(['result_defender','result_attacker'],as_index = False).agg({'n':'sum'})
  df_result['proc'] = df_result['n'] / sum(df_result['n'])
  return df_result

#creating dfs with throw results for 1,2 and 3 dices.
#Remember, we keep only two best results, even when throwing 3 dices.
one_dice_combs = get_dice_combs(1)
two_dice_combs = get_dice_combs(2)
three_dice_combs = get_dice_combs(3)

##creating dataframes with results for attacker and defender when attacker uses 1,2 or 3 dices 
##and defender uses 1 or 2 dices (according to Risk boardgame rules)
att_def_combs = {}
for defender_dice in range(1,3):
  #print(defender_dice)
  for attacker_dice in range(1,4):
    df = get_chances_from_combs(get_dice_combs(defender_dice),get_dice_combs(attacker_dice))
    att_def_combs[str(defender_dice)+'on'+str(attacker_dice)] = df
del(defender_dice)
del(attacker_dice)

def calculate_odds(natt,ndef,att_def_combs,odds_matrix):
    """
    Arguments:
        number of attackers, 
        number of defenders, 
        dict with dfs of dice rolls results,
        odds_matrix, with odds for winning - must be filled for all battles with lower number of attackers and defenders
    Returns winning chances for attacker 
    """
    df = att_def_combs[str(min(ndef,2))+'on'+str(min(natt-1,3))]
    
    win_row = df[df['result_attacker'] > df['result_defender']].values.flatten().tolist()
    win_odds = win_row[3]
    if ndef + win_row[0]==0:
        after_win_odds = 1
    else:
        after_win_odds = [odds[1] for odds in odds_matrix if odds[0] == [natt + win_row[1],ndef + win_row[0]]][0]
    
    draw_row = df[df['result_attacker'] == df['result_defender']].values.flatten().tolist()
    if len(draw_row)==0:
        draw_odds = 0
        after_draw_odds = 0
    elif ndef + draw_row[0]==0:
        draw_odds = win_row[3]
        after_draw_odds = 1        
    elif natt + draw_row[1]<2:
        draw_odds = win_row[3]
        after_draw_odds = 0
    else:   
        draw_odds = draw_row[3]
        after_draw_odds = [odds[1] for odds in odds_matrix if odds[0] == [natt + draw_row[1],ndef + draw_row[0]]][0]
    
    lost_row = df[df['result_attacker'] < df['result_defender']].values.flatten().tolist()
    lost_odds = lost_row[3]
    if natt + lost_row[1]<2:
        after_lost_odds = 0
    else:
        after_lost_odds = [odds[1] for odds in odds_matrix if odds[0] == [natt + lost_row[1],ndef + lost_row[0]]][0]
    odds = win_odds * after_win_odds + draw_odds * after_draw_odds + lost_odds * after_lost_odds
    return odds

##finally, we will create a list with winning chances for all combinations of number of attackers and defeders
##each element of list is a list with: 
    #-first element storing number of attackers and defenders in a list
    #-second element storing winning chances for attacker 
##e.g. element [[0,1],0] means that for 0 attackers and 1 defender attacker has 0 chances for winning. 
##we will manually fill first three elements of list, with all combinations for 0 and 1 attackers and defenders.
odds_matrix_starter =\
[\
[[0,1],0],\
[[1,0],1],\
[[1,1],0],\
]

    ## all other elements will be filled automatically using calculate_odds function 

def update_odds_matrix(max_natt,max_ndef,odds_matrix_starter):
    for natt in range(2,max_natt+1):
        for ndef in range(1,max_ndef+1):
            odds = calculate_odds(natt,ndef,att_def_combs,odds_matrix_starter)
            odds_list =[[natt,ndef],odds]
            odds_matrix_starter.append(odds_list)
    return(odds_matrix_starter)

odds_matrix = update_odds_matrix(30,30,odds_matrix_starter)

#finally lets create a data frame to make some visualizations
df_odds = pd.DataFrame(columns = ['att','def','win'])
for row in range(len(odds_matrix)):
  df_odds.loc[len(df_odds.index)] = [odds_matrix[row][0][0],odds_matrix[row][0][1],odds_matrix[row][1]]

os.getcwd()
os.chdir('C:\\Users\\ppodl\\Desktop\\praca\\20230221_risk_boardgame')
df_odds['win_rounded'] = round(df_odds['win'],3)
df_odds.to_csv('odds_MOD.csv',index = False,sep=';',decimal = ',')



df_odds['win_chance'] = round(df_odds['win'],2)*100
df_odds['win_chance'] = df_odds['win_chance'].astype(str)


ggplot(df_odds[(df_odds['win']>.2) & (df_odds['win']<.8)], aes(x='att', y='def',fill = 'win')) +\
geom_tile() +\
geom_label(aes(label= 'win_chance')) +\
scale_fill_gradient(low="red",high="darkgreen")


?to_csv


import seaborn
from pathlib import Path
print(Path.cwd())
import pathlib
pathlib.Path().absolute()
os.path.realpath(__file__)
