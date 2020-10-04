'''
Create the gold transcription files for the Common Voice dataset
wget https://common-voice-data-download.s3.amazonaws.com/cv_corpus_v1.tar.gz
'''

import glob
import re
import os
import shutil
import pandas as pd


def main():
    data_folder = os.path.join('..', 'data', 'common-voice')
    df = pd.read_csv(os.path.join('..', 'data', 'clips_202010021436.csv'))
    out_folder = os.path.join('..', 'data', 'vinbrain')

    for index, row in df.iterrows():
        speech_filepath = row['path']
        print('speech_filepath: {0}'.format(speech_filepath))
        speech_filename = speech_filepath.split('/')[-1][:-4]
        print('speech_filename: {0}'.format(speech_filename))
        speech_user = re.sub('-', '_', speech_filepath.split('/')[0]).split('_')[4]
        gold_transcription_filepath_text = os.path.join(out_folder, speech_user + '_' + speech_filename + '_gold.txt')
        gold_transcription_file = open(gold_transcription_filepath_text, 'w')

        gold_transcription = row['sentence']
        print('os.path.basename(speech_filepath): {0}'.format(os.path.basename(speech_filepath)))
        print('gold_transcription: {0}'.format(gold_transcription))
        gold_transcription_file.write(gold_transcription)
        gold_transcription_file.close()

        shutil.copy2(os.path.join(data_folder, speech_filepath),
                     os.path.join(out_folder, speech_user + '_' + speech_filename + '.mp3'))


if __name__ == "__main__":
    main()
    # cProfile.run('main()') # if you want to do some profiling
