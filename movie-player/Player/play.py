
from shutil import which
import subprocess



class MpvPlayer:
	def __init__(self) :
		pass

	def mpv_check(self) -> bool :
		return which('mpv') is not None

	def mpv_paly(self, title : str, fullsecreen : bool, stream_url : str) -> subprocess.run:
		if self.mpv_check() :
			mpv = ['mpv',  "--no-terminal",  "--no-terminal"]

			if fullsecreen :
				mpv.append('--fs')
		
			assert stream_url is not None and title is not None

			mpv.extend([f'--force-media-title={title}', stream_url, '2>&1 dev/null' , '&'])

			return subprocess.run(mpv)

		raise NoSuchPlayerFound('no media player found in your system .')


# Errors 
class NoSuchPlayerFound(Exception):
	pass

