configuration = {
	'data_dir' : '/home/semih/svnwatch',
	'temp_dir' : '/home/semih/svnwatch',
	'smtp' : {
		'host' 	: 'smtphost',
		'port'	: 465,
		'user' 	: 'smtpuser',
		'pass' 	: 'smtppass',
		'secure': True,
		'sender': 'from@emailaddr.com'
	},
	'email_recipients' : (
		'recipient@emailaddr.com',
	),
	'repositories' : (
		{
			'addr' : 'svn://repoaddr.com', 
			'name' : 'repo-name', 
			'start_revision' : 100,
			'watch_users' : ('james', 'jack', 'joe')
		},
	)
}

