#!/home/josef/apps/anaconda/bin/python

"""
Standalone or importable way to split a large flac file by it's cue file
As often happens when downloading from lazy people on Demonoid
"""

import sys,os,subprocess,re



class track:
    """
    A cue audio track
    """
    
    def __init__(self,num):
        
        self._num         = num
        self._seek_index  = ""
        self.tags         = {'TRACK':num}
        
        
    def __str__(self):
        return 'TRACK:{0}; TIME_INDEX:{1};'.format(self.num,self._seek_index)
        
        
        
    @property
    def num(self):
        return self._num
    
    @num.setter
    def num(self,value):
        self._num = value
        
    @property
    def seek_index(self):
        return self._seek_index
    
    @seek_index.setter
    def seek_index(self,value):
        self._seek_index = value
        

    
    
    
class cuesheet:
    """
    cuesheet
    Store cuesheet properties
    """
    
    def __init__(self,cue_file):
        
        self.cue_file   = cue_file    
        self.f_path     = os.path.split(cue_file)[0]
        self.audio_file = ""
        #self.cover_image= None
        self.tags       = {}
        self.tracks     = []
        self.t          = track(00)
        
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
                                    
                if line.startswith('REM GENRE'):
                    self.tags['GENRE'] = line.split(' ')[2].strip()

                if line.startswith('REM DATE'):
                    self.tags['DATE'] = line.split(' ')[2].strip()
                
                if line.startswith('TITLE'):
                    self.tags['ALBUM'] = re.sub( "[^a-zA-Z0-9 \.]","",line.split('"')[1].strip() )                 
                

                
            f.seek(0)
            for line in f.readlines():

                if "TRACK" in line:
                    self.t = track(line.split(" ")[3])
                    self.t.tags.update(self.tags)
                                        
                if "TITLE" in line:
                    self.t.tags['TITLE'] = line.split('\"')[1].strip().replace('\'','')
                    
                if "PERFORMER" in line:
                    self.t.tags['ARTIST'] = line.split('"')[1]
                    
                if "INDEX" in line:
                    self.t.seek_index = '{0}:{1}.{2[0]}{2[1]}'.format(*line.split(' ')[6].split(':'))

                    self.tracks.append(self.t)


                
        
    def __str__(self):
        return 'CUESHEET:{0}'.format(self.cue_file)

    def img_parse(self,new_image_out_path):
        """
        xxx
        """
        i_file = os.path.join(self.f_path,'cover.jpg')
        if os.path.isfile( i_file ):
            
            from PIL import Image
            i_img = Image.open(i_file)
            #if i_img.size[0] > 500:
            resize_ratio = 500/i_img.size[0]
            resize_width = int(resize_ratio*i_img.size[0])
            resize_height= int(resize_ratio*i_img.size[1])
            resized_img = i_img.resize( (resize_width, resize_height), Image.ANTIALIAS )
            resized_img.save(os.path.join(new_image_out_path,'folder.jpg'))
            #self.cover_image = os.path.join(self.f_path,'folder.jpg')
                
            #else:
            #    self.cover_image = default_cover_image
                
        
        
def main(argv):
    
    i_cue_file = argv[1]
    o_new_files= argv[2]
    
    
    if not os.path.isfile(i_cue_file):
        exit("Cannot file cue file: " + i_cue_file)
    else:
        cs = cuesheet(i_cue_file)     
        cs.cue_parse()
        
        
        new_f_path = os.path.join(o_new_files,cs.tags['ALBUM'] )
        if not os.path.exists(new_f_path):
            os.makedirs(new_f_path)
        
        cs.img_parse(new_f_path)
        
        
        # TODO: if cover.jpg put that into cuesheet object or just directly into cmdline 
        # however, i'll first have to check for resolution on that cover.jpg and reduce it to 500
        # TODO: output file names
        
        
        # process each cue track
        # loop using an index so we can get data from previous or next track         
        for track_indx in range(len(cs.tracks)):
                        
            # check for existing first 
            new_file = '{0}{1}track{2}.flac'.format(new_f_path,os.path.sep,cs.tracks[track_indx].num)
            if not os.path.isfile(new_file):

                # initiate command by dumping out all tags
                cmd = 'flac --silent --compression-level-6 ' + ' '.join("--tag={!s}={!r}".format(key,val) for (key,val) in cs.tracks[track_indx].tags.items() )
               
                if track_indx == 0:
                    cmd = cmd + ' --until={0}'.format(cs.tracks[track_indx+1].seek_index)
                    
                elif track_indx == len(cs.tracks)-1:    
                    cmd = cmd + ' --skip={0}'.format(cs.tracks[track_indx].seek_index)
                    
                else:
                    cmd = cmd + ' --skip={0} --until={1}'.format(cs.tracks[track_indx].seek_index, cs.tracks[track_indx+1].seek_index)
                
                
                if os.path.isfile(os.path.join(new_f_path,'folder.jpg')):
                    cmd = cmd + ' --picture='+os.path.join(new_f_path.replace(' ', '\ '),'folder.jpg')
                    
                    
                cmd = cmd + ' --output-name={0} {1}'.format(new_file.replace(' ', '\ '), cs.audio_file)
                print(cmd)
                mf = subprocess.run(cmd, shell=True)
                if mf.returncode:
                    exit("ERROR")

            exit("DEBUG")

if __name__ == "__main__":
    main(sys.argv)
    
