# MOO2 Game Tree Search
The goal of this project is to perform a game-tree search related to the turn based strategy game Master of
Orion 2.

Most of the game logic related to the economic aspects of MOO2 has been coded in Python.
That is, colonies can be managed as in MOO2, tech fields can be researched, and food freighters can utilized.
Currently, the logic related to colony bases, colony ships, the ability to transfer colonists between planets, 
or the empire wide tax rate has not been implemented.

At the moment the game logic assumes that the player's race is democratic and creative with +2 research per scientist.

More about the game-tree search:

Let's say that our reduced version of the MOO2 has been completed if
1. Every available tech field has been researched.
2. The climate of every colony in the empire has been terraformed to gaia and has reached full population.
3. For every colony in the empire, every building, except possibly pollution processor or atmospheric renewer, 
   has been built.

The goal of this project is then to, starting at some initial game position, find a sequence of
actions of minimal length that completes the game.



