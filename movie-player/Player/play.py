import os
from shutil import which
import subprocess



class MpvPlayer:
	def mpv_check(self) -> bool :
		return which('mpv') is not None

	def mpv_paly(self, title : str, fullsecreen : bool, stream_url : str) -> subprocess.Popen:
		if self.mpv_check() :
			mpv = ['mpv',  "--no-terminal"]

			if fullsecreen :
				mpv.append('--fs')
		
			mpv.extend([f'--force-media-title={title}', stream_url])
			stdout = open(os.devnull, 'w')
			return subprocess.Popen(mpv, stdout=stdout, stderr=subprocess.STDOUT)

		raise NoSuchPlayerFound('mpv player not found in your system .')

class VlcPlayer:
	def vlc_check(self) -> bool:
		return which('vlc') is not None

	def vlc_play(self, title : str, fullsecreen : bool, stream_url : str) -> subprocess.Popen:
		if self.vlc_check:
			vlc = ['vlc', '--no-video-title-show']
			if fullsecreen:
				vlc.append('--fullscreen')
			vlc.extend([f'--meta-title={title}', stream_url])
			stdout = open(os.devnull, 'w')
			return subprocess.Popen(vlc, stdout=stdout, stderr=subprocess.STDOUT)
		raise NoSuchPlayerFound('vlc player not found in your system .')

# Errors 
class NoSuchPlayerFound(Exception):
	pass

