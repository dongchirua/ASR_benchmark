for f in ../data/vinbrain/*.mp3; do
    ffmpeg -i ${f%.*}.mp3 -acodec pcm_s16le -ac 1 -ar 16000 ${f%.*}.wav -y;
    rm ${f%.*}.mp3
done