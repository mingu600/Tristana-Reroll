import gradio as gr
import pickle as pkl
import os

if __name__ == "__main__":
    min_unit = 3
    max_unit = 8
    min_gold = 40
    max_gold = 51
    with open('plot_dict.pkl', 'rb') as handle:
        plot_dict = pkl.load(handle)


    def gradio_f(trade_sector, number_of_duplicators, number_of_tristanas, number_of_maokais, number_of_poppys, number_of_viegos, amount_of_gold):
        f_input = (trade_sector, number_of_duplicators, number_of_tristanas, number_of_maokais, number_of_poppys, number_of_viegos, amount_of_gold)
        return plot_dict[f_input][0], plot_dict[f_input][1]

    demo = gr.Interface(fn=gradio_f, title='Tristana Reroll (intended for use on 3-1)', allow_flagging = 'never', inputs = [gr.Checkbox(label="Trade Sector", info="Check if Trade Sector was taken"), gr.Checkbox(label="Training Reward", info="Check if you are planning on taking Training Reward"), gr.Slider(min_unit, max_unit, value=min_unit + 2, label="Tristana", info="Choose number of owned Tristanas (between 3 and 8)", step=1), gr.Slider(min_unit, max_unit, value=min_unit + 1, label="Maokai", info="Choose number of owned Maokais (between 3 and 8)", step=1),
    gr.Slider(min_unit, max_unit, value=min_unit + 1, label="Poppy", info="Choose number of owned Poppys (between 3 and 8)", step=1), gr.Slider(min_unit, max_unit, value=min_unit + 2, label="Viego", info="Choose number of owned Viegos (between 3 and 8)", step=1), gr.Slider(min_gold, max_gold - 1, label = 'Gold', info='Amount of starting gold on 3-1', step=5)], outputs = [gr.Plot(label='Counts', info='Histogram of simulations'), gr.Plot(label='Probability plot', info='Success Probability')])
    demo.launch(share=True)