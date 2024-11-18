How to run whisper.cpp on windows ? 


Prerequisites with Path set: 
1. Git
2. Cmake
3. MSBuild tools for C++ development ( contains C++ compiler)
4. ffmpeg

Run the following commands in a command prompt: 
```
1. git clone https://github.com/ggerganov/whisper.cpp.git
2. cd whisper.cpp
3. cmake . --fresh
4. msbuild ALL_BUILD.vcxproj /p:Configuration=Release
5. cd models
6. curl -L https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.en.bin?download=true -o models\ggml-tiny.en.bin
7. (Copy all files from bin/Release to whisper.cpp)

8. main -m models\ggml-base.bin -f samples/jfk.wav -t 8
```

The last command should print the transcription<br> 
[00:00:00.000 --> 00:00:11.000]   And so my fellow Americans, ask not what your country can do for you, ask what you can do for your country.
