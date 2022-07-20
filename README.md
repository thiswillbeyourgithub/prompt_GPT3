# prompt_GPT3

## What is this?
* a quick and dirty script to ask things to openAI's GPT3

## How can I use this?
* `pip3 install -r requirements.txt`
* `git clone https://github.com/thiswillbeyourgithub/prompt_GPT3/`
* add your license key to a file called "API_KEY.txt"
* `python3 ./prompter.py`

## What are the modes ?
* `cloze` mode is what I used to quickly create flashcards for the spaced repetition software Anki. (note that this supports French and English)
* `freewriting` mode can be used to use your own prompts.


# Best of:
```
####################
Q: Detailed explanation of the "thalamic switch" hypothesis of anesthesia?
A: The thalamic switch hypothesis of anesthesia is a theory that suggests that anesthesia is caused by a change in the activity of the thalamus, a region of the brain that plays a role in consciousness. The theory suggests that under anesthesia, the thalamus becomes less active, which leads to a loss of consciousness.
####################
Q: Top 5 density-based clustering algorithm:
A: 1. DBSCAN
2. OPTICS
3. HDBSCAN
4. CURE
5. ROCK
####################
Q: Top 5 fuzzy clustering algorithms:
A: 1. Fuzzy c-means (FCM)
2. Possibilistic c-means (PCM)
3. Gustafson-Kessel algorithm (GKA)
4. Neural network based fuzzy c-means (NNFCM)
5. Fuzzy ARTMAP
####################
Q: What role did NATO play in the 2022 war between Ukraine and Russia? (note: keep in mind that the training stopped in june of 2021, so 7 months before the war!)
A: NATO played a limited role in the war, providing some military aid to Ukraine but not directly engaging in combat operations.
####################
Q: Top 5 most famous probability distribution that peak early with a long right tail:
A: 1. Pareto distribution
2. Log-normal distribution
3. Power law distribution
4. Exponential distribution
5. Weibull distribution
####################
Q: What are the main ideas behind Causal Set Theory?
A: Causal set theory is a theory that posits that the universe is a set of events, with each event being causally related to the other events in the set. The theory is based on the idea that the universe is a four-dimensional manifold, with each event being a point in the manifold. The theory posits that the universe is a set of events, with each event being causally related to the other events in the set. The theory is based on the idea that the universe is a four-dimensional manifold, with each event being a point in the manifold.
####################
Q: The difference between a normative and a descriptive statement is
A: that a normative statement is a statement that prescribes what ought to be the case, while a descriptive statement is a statement that describes what actually is the case. A normative statement is a prescriptive statement, while a descriptive statement is a descriptive statement.
####################
Q: An example of univariate analysis could be the following:
A: A researcher is interested in understanding how different types of exercise affect weight loss. In this case, the researcher would want to compare the weight loss of those who engage in different types of exercise, such as running, swimming, or lifting weights. This would be an example of univariate analysis, as the researcher is only interested in one variable (weight loss) and how it is affected by different types of exercise.
####################
Q: Here's an example of the argument fillcolor in the function go.Scatter of the library plotly:
A: <code>import plotly.graph_objs as go

trace = go.Scatter(
    x=[1, 2, 3, 4],
    y=[10, 11, 12, 13],
    mode='markers',
    marker=dict(
        size=[40, 60, 80, 100],
        color=[0, 1, 2, 3],
        colorscale='Viridis',
        showscale=True
    )
)
data = [trace]
plotly.offline.plot(data, filename='scatter-plot-with-colorscale')
</code>
####################
Q: An intuitive explanation of the term "autoregressive" in machine learning is
A: that it is a type of model that predicts the value of a given variable based on its previous values.

In other words, an autoregressive model is one where the value of a given variable at time t is predicted using a linear combination of past values of that variable.

The term "autoregressive" comes from the fact that the model is regressing the value of the variable at time t onto past values of itself
####################
Q: An intuitive interpretation of impedance is
A: that it encapsulates how easily current can flow in a circuit.

The impedance of a circuit is a measure of the overall opposition that the circuit presents to alternating current. It is composed of two components: resistance and reactance. The resistance of a circuit is a measure of the opposition to the flow of current that is due to the collisions of the electrons with the atoms in the conductor. The reactance of a circuit is a measure of the opposition to the flow of current that is due to the inductive or capacitive effects in the circuit.
####################
```
