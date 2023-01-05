const mongoose = require("mongoose");
const dotenv = require("dotenv");
dotenv.config({ path: "../config.env" });
const fetch = require("node-fetch");
const User = require("../Models/UserAccountSettings");



const DB = process.env.DATABASE.replace(
  "<PASSWORD>",
  process.env.DATABASE_PASSWORD
);

console.log(DB);
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

async function getData() {
  try {
    const body = {
      userid: process.env.TOKEN_LOGIN_USERNAME,
      password: process.env.TOKEN_LOGIN_PASSWORD,
    };
    const URL = "http://127.0.0.1:8000/api/v1/user/login";
    const tokenData = await fetch(URL, {
      method: "POST",
      body: JSON.stringify(body),
      headers: { "Content-Type": "application/json" },
    }).then((res) => res.json());

    const url = "http://127.0.0.1:8000/api/v1/userAccount";
    const data = await fetch(url, {
      method: "get",
      headers: {
        Authorization: "Bearer " + tokenData.token,
      },
    }).then((res) => res.json());
    data.forEach(async function (el) {
      try {
        const follower = `http://127.0.0.1:8000/api/v1/follower?user_id=${el.user_id}`;
        const following = `http://127.0.0.1:8000/api/v1/following?user_id=${el.user_id}`;
        const post = `http://127.0.0.1:8000/api/v1/post?userid=${el.user_id}`;
        var pdata = await fetch(post, {
          method: "get",
          headers: {
            Authorization: "Bearer " + tokenData.token,
          },
        }).then((res) => res.json());
        var fdata = await fetch(follower, {
          method: "get",
          headers: {
            Authorization: "Bearer " + tokenData.token,
          },
        }).then((res) => res.json());
        var fodata = await fetch(following, {
          method: "get",
          headers: {
            Authorization: "Bearer " + tokenData.token,
          },
        }).then((res) => res.json());

        // fdata = JSON.stringify(fdata);
        //console.log(JSON.parse(fdata)[0].followers.length);
        // fdata = JSON.parse(fdata);
        let DATA;
        if (pdata.length == 0) {
          var update = { posts: 0 };
          const filter = { user_id: el.user_id };
          await User.findOneAndUpdate(
            filter,
            update,
            { new: true },
            (err, data) => {
              if (err) {
                console.log(err);
              }
            }
          );
        }
        if (fdata.length == 0 || fdata[0].followers.length == 0) {
          var update = { followers: 0 };
          const filter = { user_id: el.user_id };
          await User.findOneAndUpdate(
            filter,
            update,
            { new: true },
            (err, data) => {
              if (err) {
                console.log(err);
              }
            }
          );
        }
        if (fodata.length == 0 || fodata[0].Following.length == 0) {
          var update = { following: 0 };
          const filter = { user_id: el.user_id };
          await User.findOneAndUpdate(
            filter,
            update,
            { new: true },
            (err, data) => {
              if (err) {
                console.log(err);
              }
            }
          );
        }
        if (
          !(typeof fdata[0] === "undefined") ||
          !(typeof fodata[0] === "undefined")
        ) {
          //console.log(fdata[0].followers.length);
          if (fdata[0].followers.length > 0) {
            var update = {
              followers: fdata[0].followers.length,

              posts: pdata.length,
            };
            const filter = { user_id: el.user_id };
            //console.log(fdata[0].followers.length);
            DATA = await User.findOneAndUpdate(
              filter,
              update,
              { new: true },
              (err, data) => {
                if (err) {
                  console.log(err);
                }
              }
            );
          }
          if (fodata[0].Following.length > 0)
            var update = {
              followers: fdata[0].followers.length,
              following: fodata[0].Following.length,
              posts: pdata.length,
            };
          const filter = { user_id: el.user_id };
          //console.log(fdata[0].followers.length);
          DATA = await User.findOneAndUpdate(
            filter,
            update,
            { new: true },
            (err, data) => {
              if (err) {
                console.log(err);
              } else {
                console.log(" ");
              }
            }
          );
          console.log(DATA);
        }
      } catch (err) {
        console.log(err);
      }
      // const Data = await User.patch({ followers: fdata.followers.length });
      // console.log(Data);
    });
  } catch (e) {
    console.log(e);
  }
}

getData();
