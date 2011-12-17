# Deviant Art download script

This is a script to create a list of links to images in deviantART galleries/favourites/(things with lots of pictures and a next button). It doesn't actually do the downloading itself because Python isn't the best tool for the job IMHO.

## Requirements

- [Python 3](http://www.python.org/)
- [lxml](http://lxml.de/)

## Usage

- Open up a terminal/command prompt
- Go to the directory where you downloaded the script
- Type 
      python3 <Put the full URL eg. http://xxx.deviantart.com/gallery/ here> <Put the name of the output file here>
- Hit enter

You will be left with a file with the name you specified and filled with the URLs of all the images in the gallery you gave. To download them all, I suggest [Aria2](http://aria2.sourceforge.net/). To use it do do the downloading:

- Put the aria2 file in the same directory as your list
- Type 
      aria2 -i <filename of your list here> -d <output directory name here>

I'm writing this for Windows users. If you're a Linux user you can figure it out. If you're a Mac user, complain to me about it and I'll probably write something for you too :) I don't have a Mac though so I can't really do anything at the moment...

# License

Give me credit if you use my code. DA may have problems with us using this but I couldn't find anything on the subject.