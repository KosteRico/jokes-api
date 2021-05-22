from django.urls import path, include

from api.views import auth, jokes

jokes_urlpatterns = [
    path('', jokes.JokesView.as_view()),
    path('<int:id>', jokes.OneJokeView.as_view()),
    path('generate/', jokes.generate_joke),
]

urlpatterns = [
    path('login/', auth.login_view),
    path('logout/', auth.logout_view),
    path('register/', auth.register_view),
    path('jokes/', include(jokes_urlpatterns)),
]
