# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python Docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load

from collections import defaultdict, Counter
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
import random
import os
import multiprocessing
import math
import pickle as pkl
from multiprocessing import Pool
import plotly.express as px
import gradio as gr
import time

# Define unit pools and shop probabilities
one_costs = ['Cassiopeia', "Cho'gath", 'Irelia', 'Jhin', 'Kayle', 'Malzahar', 'Maokai', 'Orianna', 'Poppy', 'Renekton', 'Samira', 'Tristana', 'Viego']
two_costs = ['Ashe', 'Galio', 'Jinx', 'Kassadin', 'Kled', 'Sett', 'Soraka', 'Swain', 'Taliyah', 'Teemo', 'Vi', 'Warwick', 'Zed']
three_costs = ['Akshan', 'Darius', 'Ekko', 'Garen', 'Jayce', 'Kalista', 'Karma', 'Katarina', 'Lissandra', "Rek'Sai", 'Sona', 'Taric', "Vel'Koz"]
four_costs = ['Aphelios', 'Azir', 'Gwen', 'JarvanIV', "Kai'Sa", 'Lux', 'Nasus', 'Sejuani', 'Shen', 'Urgot', 'Yasuo', 'Zeri']
unit_name_dict = {1: one_costs, 2: two_costs, 3: three_costs, 4:four_costs}
level_prob_dict = {1: [1, 0, 0, 0], 2:[1, 0, 0, 0], 3:[0.75, 0.25, 0, 0], 4:[0.55, 0.3, 0.15, 0], 5:[0.45, 0.33, 0.2, 0.02], 6:[0.25, 0.4, 0.3, 0.05]}
g = np.random.Generator(np.random.PCG64())

def run_simulation(duplicators=0, trade_sector=1, tristana=4, maokai=4, poppy=4, viego=4, gold=50, min_threshold=20):

    # Whether we've finished rolling
    def finished_rolling(duplicators=0):
        num_left = (9 - team_counter['Tristana']) + (9 - team_counter['Maokai']) + min((9 - team_counter['Poppy']), (9 - team_counter['Viego']))
        if num_left <= duplicators:
            return True
        return False

    # Updates team count of Trist/Maokai/Poppy/Viego and gold based on shop
    def buy_units(shop, gold):
        for unit in ['Maokai', 'Tristana', 'Poppy', 'Viego']:
            # Calculate gold needed to buy interested units
            to_buy = min(9 - team_counter[unit], shop[unit], gold)
            team_counter[unit] += to_buy
            unit_dict[unit] -= to_buy
            gold -= to_buy
        return gold

    # Just a guess on whether current team wins the round
    def win_rng():
        if finished_rolling():
            return True
        elif team_counter['Tristana'] == 9 and team_counter['Maokai'] == 9:
            return random.random() < 0.5
        elif team_counter['Tristana'] == 9 or team_counter['Maokai'] == 9:
            return random.random() < 0.3
        else:
            return random.random() < 0.1

    def reroll(level):
        probs = level_prob_dict[level]
        # Rolls cost for each shop slot
        shop_cost_roll = Counter(random.choices([1, 2, 3, 4], k=5, weights=level_prob_dict[level]))
        # Draws from unit pool
        shop = []
        for unit_cost in shop_cost_roll:
            unit_pool = []
            for i, unit in enumerate(unit_name_dict[unit_cost]):
                if team_counter[unit] < 9:
                    unit_pool.append(unit_dict[unit])
                else:
                    unit_pool.append(0)
            shop += random.choices(unit_name_dict[unit_cost], k=shop_cost_roll[unit_cost], weights = unit_pool)
        return Counter(shop)

    def calc_streak_gold(streak):
        if abs(streak) >= 5:
            return 3
        elif abs(streak) == 4:
            return 2
        elif abs(streak) >= 2:
            return 1
        return 0

    #gold = np.random.randint(30, 60)
    gold = gold
    rounds = [1, 2, 3, 5, 6, 7]
    stages = [3]
    level = 4
    output = [duplicators, trade_sector]
    # Assume lose streak all of stage 2
    streak = -5
    base_income = 5
    win = 0
    team_counter = Counter({'Tristana': tristana, 'Maokai':  maokai, 'Poppy': poppy, 'Viego':  viego})
    for unit in ['Tristana','Maokai', 'Poppy', 'Viego']:
        output.append(team_counter[unit])
    unit_dict = defaultdict(int)
    for unit in one_costs:
        unit_dict[unit] = 29
    for unit in two_costs:
        unit_dict[unit] = 22
    for unit in three_costs:
        unit_dict[unit] = 18
    for unit in four_costs:
        unit_dict[unit] = 12
    for unit in ['Tristana', 'Maokai', 'Poppy', 'Viego']:
        unit_dict[unit] -= team_counter[unit]
    roll_threshold = min_threshold
    output.append(gold)
    output.append(roll_threshold)
    for stage in stages:
        for curr_round in rounds:
            # Calculate player level given standard levelling pattern
            if stage == 3 and curr_round == 2:
                level = 5
            #print('Stage: ' + str(stage) + ', Round: ' + str(curr_round) + ', Level: ' + str(level) + ', Gold: ' + str(gold) + ', Streak: ' + str(streak))
            # Initial shop
            for i in range(1 + trade_sector):
                shop = reroll(level)
                #print('Shop: ' + str(shop))
                if not finished_rolling(duplicators):
                    gold = buy_units(shop, gold)
                #print(team_counter)
                #Roll random number of times if still not finished
                #print('Gold: ', gold)

            if stage == 3 and curr_round == 1:
                if not finished_rolling(duplicators):
                    #print('Roll Threshold: ', str(roll_threshold))
                    while True:
                        if (not finished_rolling(duplicators)) and (gold > roll_threshold):
                            gold -= 2
                            shop = reroll(level)
                            #print('Shop: ', shop)
                            gold = buy_units(shop, gold)
                            #print(team_counter)
                            #print(gold)
                        else:
                            break
            elif stage == 3 and curr_round < 5 and not finished_rolling(duplicators) and gold > 52:
                if curr_round == 2 and duplicators > 0:
                    gold += 11
                while True:
                    if (not finished_rolling(duplicators)) and (gold > 52):
                        gold -= 2
                        shop = reroll(level)
                        #print('Shop: ', shop)
                        gold = buy_units(shop, gold)
                        #print(team_counter)
                        #print(gold)
                    else:
                        break

            elif stage == 3 and curr_round == 5 and not finished_rolling(duplicators):
                while True:
                    if (not finished_rolling(duplicators)) and (gold > 23):
                        gold -= 2
                        shop = reroll(level)
                        #print('Shop: ', shop)
                        gold = buy_units(shop, gold)
                        #print(team_counter)
                        #print(gold)
                    else:
                        break


                break

            win = int(win_rng())
            if win == 0 and streak > 0:
                streak = -1
            elif win == 0 and streak < 0:
                streak -= 1
            elif win == 1 and streak > 0:
                streak += 1
            else:
                streak = 1

            # Calculate gold earned (in game it's beginning of round, for simplicity it's calculated here)
            interest = min(5, gold // 10)
            streak_gold = calc_streak_gold(streak)
            gold += base_income + interest + streak_gold + win
            

    if finished_rolling(duplicators) and gold >= 22:
        output.append(1)
    else:
        output.append(0)
    return output



if __name__ == "__main__":
    out_file_name = 'trist_reroll.pkl'
    n_games = 201
    min_unit = 3
    max_unit = 8
    min_gold = 40
    max_gold = 51
    all_games = [(duplicators, trade_sector, tristana, maokai, poppy, viego, gold, min_threshold) for duplicators in [0, 1] for trade_sector in [0, 1] for tristana in range(min_unit, max_unit + 1) for maokai in range(min_unit, max_unit + 1) for poppy in range(min_unit, max_unit + 1) for viego in range(min_unit, max_unit + 1) for gold in range(min_gold, max_gold, 5) for min_threshold in range(4, 41, 2)] * n_games
    
    if os.path.exists(out_file_name):
        with open(out_file_name, 'rb') as handle:
            stage_3_1_dict = pkl.load(handle)
    else:
        stage_3_1_dict = {'Duplicators': [], 'Trade Sector': [],'Tristana': [], 'Maokai': [], 'Poppy':[], 'Viego':[], 'Gold': [], 'Minimum gold on 3-1':[], 'Success': []}
    #print(len(stage_3_1_dict['Success']))
    startTime = time.time()
    # for game in all_games:
    #     output = run_simulation(*game)
    #     for i, key in enumerate(stage_3_1_dict):
    #         stage_3_1_dict[key].append(output[i])
    with Pool(processes=6) as pool:
        # Run simulations in parallel
        for output in pool.starmap(run_simulation, all_games):
            for i, key in enumerate(stage_3_1_dict):
                stage_3_1_dict[key].append(output[i])
    executionTime = (time.time() - startTime)
    print('Execution time in seconds: ' + str(executionTime))
    with open(out_file_name, 'wb') as handle:
        pkl.dump(stage_3_1_dict, handle)
    stage_3_1_df = pd.DataFrame.from_dict(stage_3_1_dict)
    #stage_3_1_df.to_csv('stage_3_1.csv', index=False)

    def plot_results(trade_sector, number_of_duplicators, number_of_tristanas, number_of_maokais, number_of_poppys, number_of_viegos, amount_of_gold):
        filtered_df = stage_3_1_df.loc[(stage_3_1_df['Duplicators'] == number_of_duplicators) & (stage_3_1_df['Trade Sector'] == trade_sector) & (stage_3_1_df['Gold'] == amount_of_gold)  & ((stage_3_1_df['Tristana'] == number_of_tristanas) & (stage_3_1_df['Maokai'] == number_of_maokais) | (stage_3_1_df['Tristana'] == number_of_maokais) & (stage_3_1_df['Maokai'] == number_of_tristanas)) & ((stage_3_1_df['Poppy'] == number_of_poppys) & (stage_3_1_df['Viego'] == number_of_viegos) | (stage_3_1_df['Poppy'] == number_of_viegos) & (stage_3_1_df['Viego'] == number_of_poppys))]
        fig1 = px.histogram(filtered_df, x = 'Minimum gold on 3-1', color = 'Success', color_discrete_sequence=["red", "blue"], category_orders={"Success": [0, 1]},nbins=20)
        #fig1.update_xaxes(range=[4, 35])
        success_df = pd.DataFrame(data = set(filtered_df['Minimum gold on 3-1']), columns = ['Minimum gold on 3-1'])
        success_df = success_df.sort_values(by=['Minimum gold on 3-1'])
        success_probs = []
        for x in success_df['Minimum gold on 3-1']:
            temp_df = filtered_df.loc[filtered_df['Minimum gold on 3-1'] == x]
            success_probs.append(sum(temp_df['Success'] == 1) / len(temp_df))
        success_df['Probability of success'] = success_probs

        fig2 = px.line(success_df, x='Minimum gold on 3-1', y = 'Probability of success')
        #fig2.update_xaxes(range=[4, 30])
        return fig1, fig2
    
    display_games = [(trade_sector, duplicators, tristana, maokai, poppy, viego, gold) for duplicators in [0, 1] for trade_sector in [0, 1] for tristana in range(min_unit, max_unit + 1) for maokai in range(min_unit, max_unit + 1) for poppy in range(min_unit, max_unit + 1) for viego in range(min_unit, max_unit + 1) for gold in range(min_gold, max_gold, 5)]
    plot_dict = {}
    for i, game in enumerate(display_games):
        trade_sector, duplicators, tristana, maokai, poppy, viego, gold = game
        if i % 100 == 0:
            print(i)
        if game not in plot_dict:
            plot_dict[game] = plot_results(*game)
            input2 = (trade_sector, duplicators, maokai, tristana, poppy, viego, gold)
            input3 = (trade_sector, duplicators, tristana, maokai, viego, poppy, gold)
            input4 = (trade_sector, duplicators, maokai, tristana, viego, poppy, gold)
            plot_dict[input2] = plot_dict[game]
            plot_dict[input3] = plot_dict[game]
            plot_dict[input4] = plot_dict[game]

    with open('plot_dict.pkl', 'wb') as handle:
        pkl.dump(plot_dict, handle)
