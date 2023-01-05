#script
time=$(date +"%d-%b-%Y") && \
echo "MongoDB Backup Started : $time" && \
echo "Collecting Data from Development DataBase" && \
mongodump --uri=mongodb://revmeup-staging:revmeup123@15.206.81.97:27017/revmeup?authSource=revmeup&readPreference=primary&appname=MongoDB%20Compass&ssl=false && \
wait &&\
echo "Data is stored in 'dump/revmeup'" && \
echo "Ziping the file to upload to S3" && \
filename=$(date +"backup-%d-%b-%Y.zip") && \
zip -r "$filename" dump/revmeup && \
wait &&\
echo "Ziping complete, filename: $filename" && \
echo "Trying to upload to S3" && \
aws s3 cp "$filename" s3://revmeup-mongodb-backup/ && \
wait &&\
echo "Upload Complete"