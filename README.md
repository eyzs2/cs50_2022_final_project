# SPOTIPSYCHIC
#### Video Demo: https://youtu.be/hQ48j33pZyk
#### Description:
The project is a website aiming to take advantage of the Spotify API to provide insights into a user's listening history.

The website prompts the user to provide authorisation via OAuth, allowing the server to access user data, including the user's top tracks, current favourites, and recommends users tracks using the recommendation functions included within the Spotify API. The backend is written in **Python**, implementing the Spotipy library to access and communicate with the Spotify API. The application is primarily based in **Flask**, whereas the frontend implements a limited amount of **JavaScript and jQuery** for content display. Jinja is also used to parse data between the server- and client-side.

Before the webpage is used, a Client ID and Client Secret must be provided via export SPOTIPY_CLIENT_ID and export SPOTIPY_CLIENT_SECRET. These can be obtained by registering using the Spotify API Developer Tools using one's Spotify account.


###### Login:
Before the main functionalities of the website are accessed by the user, users are redirected to /login and indexed.html is rendered, allowing users to authorise the application's access to their data. This is managed by the login() function. Only after this authorisation is provided can users access the website via redirect from /callback, rendering / and rendering index.html. The authorisation is managed by the auth_manager() function. Any further access of any of the features is managed by the @login_required function, which prevents users from bypassing the login by simply typing the desired path into the URL.

When a user logs in, the application caches the user's data in the ./spotify_caches folder. If the folder does not exist, the application creates the folder.

The main functionality of the website can be distinguished into the ***Music Past*** and ***Music Future*** sections, which are presented to the user as pathways at the homepage.

###### Music Past:
The Music Past section takes the user's most listened to tracks and performs an audio analysis on the top 20 all-time tracks of the user using Spotify's built-in analysis tool, returning the acousticness, danceability and energy of each track as defined in [Spotify's Developer Website](https://developer.spotify.com/documentation/web-api/reference/#/operations/get-several-audio-features). Different calculations such as standard deviation and averages of the values are undertaken, presenting different statements to the user based on the findings of the analysis, which are rendered in musicpast.html. This is managed by the musicpast() function.

###### Music Future:
The Music Future section takes a few of the user's current most-listened to tracks and artists and uses them as inputs into Spotify's built-in [recommendations function](https://developer.spotify.com/documentation/web-api/reference/#/operations/get-recommendations), after which returning the tracks in a playlist format in /musicfuture in musicfuture.html. By clicking the button above the playlist, the website posts the data and the playlist shown is added to their own personal Spotify Library, rendering musicfutureadded.html. This is managed by the musicfuture() function, which observes the method the user utilises to request, and responds accordingly. As the recommendations are refreshed every time the user requests /musicfuture by GET, for the same playlist to be added to the user's library, the recommended tracks are parsed by musicfuture() when it receives a POSt request, allowing for the same playlist that the user observes on the site to be added to their library.

###### Logout:
In every page the logout link is included, which logs users out of their Spotify account, clearing the cache and allowing a new user to input their account and access the site. This is managed by the logout() function.