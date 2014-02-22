# Create your views here.
from django.http import HttpResponse
from django.template import RequestContext, loader
import soundcloud

# Index will contain a form for entering user information to generate the playlist.
def index(request):
	template = loader.get_template('hangouts/index.html')
	context = RequestContext(request, {},)
	return HttpResponse(template.render(context))

# Given a request, returns a list containing all the entered soundhound user ids.
def get_users(client, request):
	ids = []
	# Each user input has the name with the format user_name#.
	for key,val in request.POST.iteritems():
		if "user_name" in key:
			user_id = client.get('/resolve', url='https://soundcloud.com/' + val).id
			ids.append(user_id)
	return ids

def get_sorted_tracks(client, ids):
	tracks = []
	track_ids = {}
	# Find all tracks that users have favourited.
	for user in ids:
		tracks = tracks + list(client.get('/users/' + str(user) + '/favorites'))
	print "Users: ",
	print ids
	print "Tracks: ",
	print tracks
	# Count how many users have favourited each song.
	for t in tracks:
		print t.title, t.id
		if t.id in track_ids:
			track_ids[t.id] += 1
		else:
			track_ids[t.id] = 1

	print track_ids

	# Return a list of sorted track ids based on each songs rank.
	sorted_tracks = sorted(track_ids, key=track_ids.get)
	sorted_tracks.reverse()
	print sorted_tracks
	return sorted_tracks

# Playlist will contain a customized soundcloud playlist.
def playlist(request):
	client = soundcloud.Client( 
		client_id='d05accec0d8806ca775fd78523f6832a',
		client_secret='e78f9f003214b112a1160561089a9182',
		username='mike_n_7',
		password='pressplay'
	)

	users = get_users(client, request)
	ranked_tracks = get_sorted_tracks(client, users)

	tracks = map(lambda id: dict(id=id), ranked_tracks)
	playlist = client.post('/playlists', playlist={
		'title': 'New playlist',
		'sharing': 'public',
		'tracks': tracks
	})

	embed_info = client.get('/oembed', url=str(playlist.permalink_url))
	template = loader.get_template('hangouts/playlists.html')
	context = RequestContext(request, {'embed_playlist': embed_info.html},)
	return HttpResponse(template.render(context))

def callback(request):
	template = loader.get_template('hangouts/callback.html')
	context = RequestContext(request, {},)
	return HttpResponse(template.render(context))