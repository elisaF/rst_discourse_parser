## FIXED: Jessy Li 05/28/15
## Change stderr reading for crf output to pipe.communicate();
## adding stdout to Popen();
## output from crf is in fact in stdout not stderr
## seems classifier's Popen has to be called every time a sentence needs to be classified
import subprocess
import paths
import os.path

class CRFClassifier:
    def __init__(self, name, model_type, model_path, model_file, verbose):
        self.verbose = verbose
        self.name = name
        self.type = model_type
        self.model_fname = model_file
        self.model_path = model_path
        
        if not os.path.exists(os.path.join(self.model_path, self.model_fname)):
            print 'The model path %s for CRF classifier %s does not exist.' % (os.path.join(self.model_path, self.model_fname), name)
            raise OSError('Could not create classifier subprocess')
        
        
        self.classifier_cmd = '%s/crfsuite-stdin tag -pi -m %s -' % (paths.CRFSUITE_PATH, 
							 os.path.join(self.model_path, self.model_fname))
        self.classifier = None
#        print self.classifier_cmd
        #self.classifier = subprocess.Popen(self.classifier_cmd, shell = True, stdin = subprocess.PIPE, stderr = subprocess.PIPE)
        
        #if self.classifier.poll():
        #    raise OSError('Could not create classifier subprocess, with error info:\n%s' % self.classifier.stderr.readline())
        
        #self.cnt = 0
            

    def classify(self, vectors):
#        print '\n'.join(vectors) + "\n\n"
        
        #self.classifier.stdin.write('\n'.join(vectors) + "\n\n")
        self.classifier = subprocess.Popen(self.classifier_cmd, shell = True, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        if self.classifier.poll():
            raise OSError('Could not create classifier subprocess, with error info:\n%s' % self.classifier.stderr.readline())
        
        #lines = []
        #line = self.classifier.stderr.readline()
        #while (line.strip() != ''):
#            print line
       #     lines.append(line)
       #     line = self.classifier.stderr.readline()
        
        stdo,stde = self.classifier.communicate('\n'.join(vectors) +"\n")
        lines = stdo.strip().split("\n")

        if self.classifier.poll():
            raise OSError('crf_classifier subprocess died')
        
        predictions = []
        for line in lines[1 : ]:
            line = line.strip()
#            print line
            if line != '':
                fields = line.split(':')
#                print fields
                label = fields[0]
                prob = float(fields[1])
                predictions.append((label, prob))
        
        seq_prob = float(lines[0].split('\t')[1])
        
        return seq_prob, predictions
    

    def poll(self):
        """
        Checks that the classifier processes are still alive
        """
        if self.classifier is None:
            return True
        else:
            return self.classifier.poll() != None
        
    
    def unload(self):
        if self.classifier and not self.poll():
            self.classifier.stdin.write('\n')
            print 'Successfully unloaded %s' % self.name
