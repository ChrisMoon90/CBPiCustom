# Basic HTTP Auth plugin for CraftBeerPi

This plugin password protects your entire CraftBeerPi installation. This is a must have if you want to make your installation globally accessible.

## Installation

Download and Install this Plugin via the CraftBeerPi user interface
or pull into the [craftbeerpi]/modules/plugins/ directory

You must install Flask-BasicAuth.

From your cbpi directory run:

`sudo pip install Flask-BasicAuth`

## Configuration

The pasword can be changed in the system parameters. However for simplicity of the code, you must restart cbpi for the password to change to take effect.

The username is `admin`
The default password is `password`
