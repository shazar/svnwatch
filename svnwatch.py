import pysvn, os, smtplib, pickle, email.utils, sys, base64
from email.mime.text import MIMEText

try:
	import config
except ImportError:
	print('Cannot find configuration file..')
	sys.exit()

def sendmail(to, subject, body, smtpinfo):
	if smtpinfo['secure']:
		smtp = smtplib.SMTP_SSL(smtpinfo['host'], smtpinfo['port'])
	else:
		smtp = smtplib.SMTP(smtpinfo['host'], smtpinfo['port'])
	
	if 'user' and 'pass' in smtpinfo:
		smtp.login(smtpinfo['user'], smtpinfo['pass'])

	# Don't check the subject, just b64 encode it...	
	headers = 'To: ' + to + '\r\n' + \
			'Subject: =?UTF-8?B?' + \
			base64.b64encode(subject.encode('utf-8')).decode('utf-8') + \
			'?=\r\n' + \
			'Date: ' + email.utils.formatdate() + '\r\n'
	
	mimetxt = email.mime.text.MIMEText(body.encode('utf-8'),
						_charset='utf-8')
	
	smtp.sendmail(smtpinfo['sender'], to, headers + mimetxt.as_string())

	
def load_status():
	try:
		f = open(config.configuration['data_dir'] + '/status.pickle', 'rb')
		status = pickle.load(f)
		f.close()
	except IOError:
		status = {}
		
	return status
	
def save_status(status):
	try:
		f = open( config.configuration['data_dir'] + '/status.pickle', 'wb')
		pickle.dump(status, f)
		f.close()

	except IOError:
		print('Cannot save state to file')
	
	return True

status = load_status()

svn = pysvn.Client()

for repo in config.configuration['repositories']:
	if not repo['addr'] in status:
		status[repo['addr']] = {}
	
	if repo['addr'] in status and 'lastrevision' in status[repo['addr']]:
		start_rev = status[repo['addr']]['lastrevision']
	else:
		start_rev = repo['start_revision']

	logs = svn.log(
					url_or_path = repo['addr'], 
					revision_start = pysvn.Revision( 
						pysvn.opt_revision_kind.number, start_rev
					),
					revision_end = pysvn.Revision(
						pysvn.opt_revision_kind.head
					)
				)
	
	for log in logs:
		if log.data['author'] in repo['watch_users']:
			if log.data['message']:
				log_message = ' '.join(log.data['message'].splitlines())
			else:
				log_message = '(no commit message)'

			email_subject = '[svnwatch] ' + repo['name'] + \
				' r' + str(log.data['revision'].number) +  ' ' + \
				log.data['author'] + ' ' + log_message
			
			if len(email_subject) > 150:
				email_subject = email_subject[:150] + '...'
			
			diff = svn.diff_peg(
				tmp_path = config.configuration['temp_dir'],
				url_or_path = repo['addr'],
				revision_start = pysvn.Revision(
					pysvn.opt_revision_kind.number, 
					log.data['revision'].number-1
				),
				revision_end = log.data['revision']
			)

			status[repo['addr']]['lastrevision'] = log.data['revision'].number

			for recipient in config.configuration['email_recipients']:
				sendmail(recipient, email_subject, 
					diff, config.configuration['smtp'])

# Now sae the status
save_status(status)


