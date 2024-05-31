#/!usr/bin/bash

if [ $# -ne 1 ]; then
cat <<EOH
Usage: $0 OUTSPEC
Where:
  OUTSPEC is one of:
  - a dir for writing a sequence of PNG files
  - a filename ending in .mp4
  - a double dash (--) for Anton's default behaviour
EOH
exit 1
fi

# H.264 file
function write_h264() {
    ffmpeg -framerate 60 -i frames_out/rbz_basic_frame-%03d.ppm -c:v libx264 -r 60 "$1"
}

function anton_default1() {
    outfile="$HOME/HOST_Documents/rbz-$(date +%Y%m%d_%H%M%S).mp4"
    write_h264 "$outfile" \
        && echo "Wrote output file: $outfile" && ls -alh "$outfile" \
        || echo "Failed to write: $outfile"
}

## Lossless FFV1 (mkv usually) file:
#function write_ffv1() {
#    ffmpeg -framerate 60 -i frames_out/rbz_basic_frame-%03d.ppm -c:v ffv1 -r 60 "$1"
#}
#
#
#function anton_default2() {
#    outfile="$HOME/HOST_Documents/rbz-$(date +%Y%m%d_%H%M%S).mkv"
#    write_ffv1 "$outfile" \
#        && echo "Wrote output file: $outfile" \
#        || echo "Failed to write: $outfile"
#}

case "$1" in
    --)
        anton_default1
        ;;

    *.mp4)
        write_h264 "$1"
        ;;

    *)
        # Convert PPM sequence to PNG sequence in $1 dir:
        # pushd frames_out
        for f in rbz_basic_frame-???.ppm; do
            echo $f
            convert $f "$1"/$f.png
        done
        # popd
        ;;
esac

