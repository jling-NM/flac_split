#!/home/josef/apps/anaconda/bin/python


import sys,os,subprocess



class track:
    
    def __init__(self,num,index,title,artist):
        
        self._num    = num
        self._index  = index
        self._title  = title
        self._artist = artist
        
        
    def __str__(self):
        return 'TRACK:{0}; TIME_INDEX:{1}; TITLE:{2}; ARTIST:{3}'.format(self.num,self.index,self.title,self._artist)
        
        
        
    @property
    def num(self):
        return self._num
    
    @num.setter
    def num(self,value):
        self._num = value
        
    @property
    def index(self):
        return self._index
    
    @index.setter
    def index(self,value):
        self._index = value
        
    @property
    def title(self):
        return self._title
    
    @title.setter
    def title(self,value):
        self._title = value

    @property
    def artist(self):
        return self._artist
    
    @artist.setter
    def artist(self,value):
        self._artist = value
    
    
class cuesheet:
    """
    cuesheet
    Store cuesheet properties
    """
    
    def __init__(self,cue_file):
        
        self.cue_file   = cue_file
        self.f_path     = ''.join(cue_file.split(os.path.sep)[0:-1])        
        self.audio_file = ""
        self.tracks     = []
        self.t = track(00,"","","")
        
    def cue_parse(self):
        """
        Parse text file into cuesheet object
        """
        
        with open(self.cue_file) as f:
            for line in f.readlines():

                if line.startswith('FILE'):
                    self.audio_file = os.path.join(self.f_path,line.split("\"")[1])
                    self.audio_file = self.audio_file.replace(' ','\\ ')
                    self.audio_file = self.audio_file.replace('(','\\(')
                    self.audio_file = self.audio_file.replace(')','\\)')
                    
                if "TRACK" in line:
                    self.t = track(00,"","","")
                    self.t.num = line.split(" ")[3]
                    
                if "TITLE" in line:
                    self.t.title = line.split('\"')[1].strip().replace('\'','')
                    
                if "PERFORMER" in line:
                    self.t.artist = line.split('"')[1]
                    
                if "INDEX" in line:
                    self.t.index = '{0}:{1}.{2[0]}{2[1]}'.format(*line.split(' ')[6].split(':'))
                    self.tracks.append(self.t)

                
                
    def get_tracks(self):
        return (track for track in self.tracks)
        
    def __str__(self):
        return 'CUESHEET:{0}'.format(self.cue_file)


def main(argv):
    
    if not os.path.isfile(argv[1]):
        exit("Cannot file cue file: " + argv[1])
    else:
        cs = cuesheet(argv[1])     
        cs.cue_parse()
        
        # if cover.jpg put that into cuesheet object or just directly into cmdline 
        # however, i'll first have to check for resolution on that cover.jpg and reduce it to 500
        
        
        for track in cs.tracks:
            print(track)
            subprocess.run("flac -t --skip={},--until={},-o track.flac "+cs.audio_file, shell=True)
        #for track in cs.get_tracks():
         #   print(track)
        
        
        #mf=subprocess.Popen(["flac","--skip={},--until={},-o track.flac ",cs.audio_file],stdout=subprocess.PIPE)
        #print(mf)
        #(cues,xxx)=mf.communicate()
        #if mf.returncode!=0:
        #    xxx            

if __name__ == "__main__":
    main(sys.argv)
    
