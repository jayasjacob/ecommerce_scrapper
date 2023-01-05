const fetch = require("node-fetch");
const Post = require("../Models/Post");
const mongoose = require("mongoose");
var AWS = require("aws-sdk");
var fs = require("graceful-fs");
const dotenv = require("dotenv");
dotenv.config({ path: "../config.env" });
const { exec } = require("child_process");
// console.log("db : " + process.env.DATABASE);
const DB = process.env.DATABASE_STAGING.replace(
  "<PASSWORD>",
  process.env.DATABASE_STAGING_PASSWORD
);

mongoose
  .connect(DB, {
    useNewUrlParser: true,
    useCreateIndex: true,
    useFindAndModify: true,
    useUnifiedTopology: true,
  })
  .then(() => {
    console.log("DB connection successful");
  });

const s3 = new AWS.S3({
  accessKeyId: "BYFNCY1E8L1LM544ZVIX",
  secretAccessKey: "UIHCWIBBFa83hezo3MthQPb3t8vEIt1BtnVBM2ql",
  endpoint: "s3.us-east-2.wasabisys.com",
});

async function getData() {
  const body = {
    userid: process.env.TOKEN_LOGIN_USERNAME_STAGING,
    password: process.env.TOKEN_LOGIN_PASSWORD_STAGING,
  };
  const URL = "https://apistaging.revmeup.in/api/v1/user/login";
  const tokenData = await fetch(URL, {
    method: "POST",
    body: JSON.stringify(body),
    headers: { "Content-Type": "application/json" },
  }).then((res) => res.json());

  const URLS = "https://apistaging.revmeup.in/api/v1/post?converted=false";
  const Data = await fetch(URLS, {
    method: "get",
    headers: {
      Authorization: "Bearer " + tokenData.token,
    },
  }).then((res) => res.json());

  //console.log(Data);
  Data.forEach(function (el) {
    try {
      var downloadedImages = new Array();
      var updateImages = new Array();
      var img = el.image_path;
      var count = 0;

      img.forEach(function (image){
        try{
          console.log(image);

        var name = image.substring(image.lastIndexOf("/") + 1).trim();
        console.log("name : " + name);
        downloadedImages.push(name);

        if (image.includes("/") && name != null && name.length > 0) {
          var convertFileCommand =
            "ffmpeg -i " +
            image +
            " -vf scale=640:-2 -movflags +faststart " +
            name;
          console.log(convertFileCommand);

          exec(convertFileCommand, (error, stdout, stderr) => {
            if (error) {
              console.log('error : ' + error.message);
              return;
            } else if (stderr || stdout) {
              count = count + 1;
            }

            console.log("size : " + downloadedImages);
            console.log("length : " + count);

            if (count == img.length) {
              downloadedImages.forEach(function (convertedImage) {
                console.log("convertedImage : " + convertedImage);
                fs.readFile(convertedImage, (err, data) => {
                  if (err) throw err;
                  const params = {
                    Bucket: "cdn.revmeup.in/userconvertedphotos/" + el.userid, // pass your bucket name
                    Key: convertedImage, // file will be saved as testBucket/contacts.csv
                    Body: data,
                    ACL: "public-read",
                  };
                  console.log(params);
                  s3.upload(params, async function (s3Err, data) {
                    if (s3Err) {
                      console.log("s3Err" + s3Err.message);
                      throw s3Err;
                    }
                    console.log(
                      `File uploaded successfully at ${data.Location}`
                    );

                    var fileLocation = data.Location.replace(
                      "s3.us-east-2.wasabisys.com/",
                      ""
                    );
                    console.log("fileLocation : " + fileLocation);
                    updateImages.push(fileLocation);

                    console.log("updateImages : " + updateImages);
                    try {
                      fs.unlinkSync(convertedImage);
                    } catch (err) {
                      console.log("err : " + err.message);
                    }

                    if (updateImages.length == downloadedImages.length) {
                      var filter = { _id: el._id };
                      var update = {
                        converted: true,
                        image_path: updateImages,
                      };

                      const DATA = await Post.findOneAndUpdate(filter, update);
                      console.log("DAATA " + DATA);
                    }
                  });
                });
              });
            }
          });
        }
        }catch(err){
          console.log(err.message);
        }
      });
    } catch (err) {
      console.log(err);
    }
  });
}
getData();
