curl --verbose --progress-bar --ipv4 --connect-timeout 8 --max-time 360 --retry 128 --ftp-ssl --disable-epsv --ftp-pasv ftp://ftp.ensembl.org/pub/release-93/json/homo_sapiens/homo_sapiens.json --output source/ensembl-protein/homo_sapiens.json