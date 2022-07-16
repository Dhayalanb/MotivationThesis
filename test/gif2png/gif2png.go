// SPDX-License-Identifier: BSD-2-Clause
// Copyright (C) 2019 by Eric S. Raymond.
package main

import (
	//"errors"
	"fmt"
	terminal "golang.org/x/crypto/ssh/terminal"
	unix "golang.org/x/sys/unix"
	"image/color"
	"image/gif"
	"image/png"
	"io"
	"os"
	"path/filepath"
	"strconv"
)

var version = "3.0.0"

var verbose int
var delete bool
var optimize bool
var preserveMtime bool
var webconvert bool
var filtermode bool
var matte bool
var matteColor color.RGBA // Was type GifColor
var numgifs int
var numpngs int

// MatteGif applies matte color to image-local transparency values
func matteGIF(img *gif.GIF, matteColor color.RGBA) {
	// The Go image library turns the GIF transparencency
	// index into an all-zeros color entry in the palette.
	// An image with such transparancy always has a local xolor trable
	if img.Config.ColorModel == nil {
		isTransparent := func(mycolor color.Color) bool {
			r, g, b, a := mycolor.RGBA()
			return r == 0 && g == 0 && b == 00 && a == 0
		}

		for i := range img.Image {
			transCount := 0
			for j := range img.Image[i].Palette {
				if isTransparent(img.Image[i].Palette[j]) {
					img.Image[i].Palette[j] = matteColor
					if verbose > 0 {
						fmt.Fprintf(os.Stderr,
							"gif2png: value %d in image %d was transparent.\n",
							j, i)
					}
				}
			}
			if transCount == 0 {
				fmt.Fprintf(os.Stderr,
					"gif2png: no transparency color in image %d, matte argument ignored\n",
					i)
			}
		}
	}
}

func writefile(img *gif.GIF, i int, out io.Writer, lastimg bool) int {
	var encoder png.Encoder
	if optimize {
		encoder.CompressionLevel = png.BestCompression
	}
	encoder.Encode(out, img.Image[i])
	return 0
}

func processfilter() int {
	img, err := gif.DecodeAll(os.Stdin)
	if err != nil {
		fmt.Fprintf(os.Stderr, "gifpng: decode error on stdin: %s\n", err)
		return 1
	}

	if numPics := len(img.Image); numPics != 1 {
		fmt.Fprintf(os.Stderr,
			"gif2png: %d images in -f (filter) mode\n", numPics)
		return 1
	}

	/* eliminate use of transparency, if that is called for */
	if matte {
		matteGIF(img, matteColor)
	}

	for i := range img.Image {
		writefile(img, i, os.Stdout, true)
		numpngs++
	}

	return 0
}

func processfile(name string, fp *os.File) int {
	var suppressDelete int
	var timeBuf []unix.Timespec

	if fp == nil {
		return 1
	}

	img, err := gif.DecodeAll(fp)
	if err != nil {
		fmt.Fprintf(os.Stderr, "gif2png: decode error on %s: %v\n", name, err)
		return 1
	}

	if preserveMtime {
		fi, err := os.Stat(name)
		if err != nil {
			return 1
		}

		// Ugh...Go doesn't have a way to retrieve access time.
		// So we'll duplicare the mod time, alas.
		ts, err := unix.TimeToTimespec(fi.ModTime())
		if err != nil {
			return 1
		}
		timeBuf = append(timeBuf, ts)
		timeBuf = append(timeBuf, ts)
	}

	fp.Close()

	numPics := len(img.Image)
	if numPics >= 0 && verbose > 1 {
		fmt.Fprintf(os.Stderr, "gif2png: number of images %d\n", numPics)
	}

	if numPics <= 0 {
		return 1
	}

	if webconvert {
		if numPics != 1 {
			fmt.Fprintf(os.Stderr, "gif2png: %s is multi-image\n", name)
			return 0
		} else {
			fmt.Printf("%s\n", name)
			return 0
		}
	}

	// eliminate use of transparency, if that is called for
	if matte {
		matteGIF(img, matteColor)
	}

	fileExt := filepath.Ext(name)
	fileStem := name[:len(name)-len(fileExt)]

	// The old version recognized _gif and _GIF suffxes, too
	if fileExt != ".gif" && fileExt != ".GIF" && fileExt != "" {
		fmt.Fprintf(os.Stderr, "gifpng: %s has an invalid extension for a GIF.\n", name)
		return 1
	}

	fileExt = ".png" // images are named .png, .p01, .p02, ...

	for i := range img.Image {
		outname := fileStem + fileExt
		fp, err := os.OpenFile(outname, os.O_WRONLY|os.O_CREATE, 0644)
		if err != nil {
			fmt.Fprintf(os.Stderr, "gifpng: can't open %s for output: %v.\n", outname, err)
			return 1
		}
		suppressDelete += writefile(img, i, fp, i == len(img.Image)-1)
		fp.Close()

		if preserveMtime {
			err = unix.UtimesNano(outname, timeBuf)
			if err != nil {
				fmt.Fprintf(os.Stderr, "gifpng: could not set output file times\n")
				return 1
			}
		}
		numpngs++
		fileExt = fmt.Sprintf(".p%02d", i+1)
	}

	if delete && suppressDelete == 0 {
		os.Remove(name)
	}
	return 0
}

func usage() {
	fmt.Fprint(os.Stderr, `\n
usage: gif2png [ -bdfghimnprstvwO ] [file[.gif]] ...

   -b  replace background pixels with given RRGGBB color (hex digits)
   -d  delete source GIF files after successful conversion
   -f  allow use as filter, die on multi-image GIF
   -m  preserve input file modification time
   -v  verbose; display conversion statistics and debugging messages
   -w  web probe, list images without animation
   -O  optimize; use zlib level 9
   -1  one-only; same as -f; provided for backward compatibility

   If no source files are listed, stdin is converted to noname.png.
`)
	fmt.Fprintf(os.Stderr, "   This is gif2png %s\n", version)
	os.Exit(1)
}

func inputIsTerminal() bool {
	return terminal.IsTerminal(int(os.Stdin.Fd()))
}

func main() {
	errors := 0
	ac := 0

	for ac = 1; ac < len(os.Args) && os.Args[ac][0] == '-'; ac++ {
		for i := 1; i < len(os.Args[ac]); i++ {
			switch os.Args[ac][i] {
			case 'b':
				if ac >= len(os.Args)-1 {
					fmt.Fprint(os.Stderr, "gif2png: missing background-matte argument\n")
					os.Exit(1)
				}
				ac++
				mycolor := os.Args[ac]
				if mycolor[0] == '#' {
					mycolor = mycolor[1:]
				}
				background, err := strconv.ParseUint(mycolor, 16, 24)
				if err != nil {
					fmt.Fprintf(os.Stderr, "gif2png: %v\n", err)
					os.Exit(1)
				}
				matteColor.R = uint8((background >> 16) & 0xff)
				matteColor.G = uint8((background >> 8) & 0xff)
				matteColor.B = uint8(background & 0xff)
				matteColor.A = 255
				matte = true
				goto skiparg

			case 'd':
				delete = true
				break

			case 'f':
				fallthrough
			case '1': /* backward compatibility */
				filtermode = true
				break

			case 'm':
				preserveMtime = true
				break

			case 'v':
				verbose++
				break

			case 'w':
				webconvert = true
				break

			case 'O':
				optimize = true
				break

			default:
				fmt.Fprintf(os.Stderr,
					"gif2png: unknown option `-%c'\n", os.Args[ac][i])
				usage()
			}
		}
	skiparg:
	}

	if verbose > 1 {
		fmt.Fprintf(os.Stderr, "gif2png: %s\n", version)
	}

	/* loop over arguments or use stdin */
	if ac == len(os.Args) {
		if inputIsTerminal() {
			usage()
		}
		if verbose > 1 {
			fmt.Fprintf(os.Stderr, "stdin:\n")
		}
		if filtermode {
			if processfilter() != 0 {
				errors++
			}
		} else {
			processfile("noname.gif", os.Stdin)
			numgifs++
		}
	} else {
		for i := ac; i < len(os.Args); i++ {
			name := os.Args[i]
			//fmt.Fprintf(os.Stderr, "gif2png: argument %s\n", name)
			fp, err := os.Open(name)
			if err != nil {
				fp, err = os.Open(name + ".gif")
				if err != nil {
					fmt.Fprintln(os.Stderr, err)
					errors++
					continue
				}
			}
			if verbose > 1 {
				fmt.Fprintf(os.Stderr, "%s:\n", name)
			}
			errors += processfile(name, fp)
			/* fp is closed in processfile */
			numgifs++
		}
	}

	if verbose > 0 {
		var legend, pluralPngs, pluralGifs string
		if errors == 0 {
			legend = "no errors detected"
		} else {
			legend = "with one or more errors"
		}
		if numpngs > 1 {
			pluralPngs = "s"
		}
		if numgifs > 1 {
			pluralGifs = "s"
		}
		fmt.Fprintf(os.Stderr, "Done (%s).  Converted %d GIF%s into %d PNG%s.\n",
			legend, numgifs, pluralGifs, numpngs, pluralPngs)
	}

	if errors > 1 {
		errors = 1
	}

	os.Exit(errors)
}
