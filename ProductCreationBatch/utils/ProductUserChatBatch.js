const fetch = require("node-fetch");
const moment = require("moment");
const mongoose = require("mongoose");
const dotenv = require("dotenv");
const Chat = require("../Models/Chat");
const ChatRoom = require("../Models/ChatRoom");
const admin = require('firebase-admin');
const serviceAccount = require('./ServiceAccountKey.json');

dotenv.config({ path: "/home/ubuntu/config.env" });

const DB = process.env.DATABASE.replace(
  "<PASSWORD>",
  process.env.DATABASE_PASSWORD
);

admin.initializeApp({
    credential: admin.credential.cert(serviceAccount),
    databaseURL: "https://revitup-86a41.firebaseio.com"
});

const firebasedb = admin.database();

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
    const pri = "https://api.revmeup.in/api/v1/user/login";
    const tokenData = await fetch(pri, {
      method: "POST",
      body: JSON.stringify(body),
      headers: { "Content-Type": "application/json" },
    }).then((res) => res.json());

    const URL = `https://api.revmeup.in/api/v1/ChatRoom?senderId=product`;
    const data = await fetch(URL, {
      method: "get",
      Accept: "application/json",
      headers: {
        Authorization: "Bearer " + tokenData.token,
      },
    }).then((res) => res.json());
    console.log('data' + data);
    data.forEach(async (el) => {
      try{  
  console.log('date' + new Date(Date.now()));
  console.log('checkeddate : ' + el.checkeddate);
  console.log('difference' + moment(new Date(Date.now())).diff(el.checkeddate, "days"));
        if (
        moment(new Date(Date.now())).format("YYYY") >=
          moment(el.createdDate).format("YYYY") &&
        moment(new Date(Date.now())).format("M") >=
          moment(el.createdDate).format("M") &&
        moment(new Date(Date.now())).diff(el.checkeddate, "days") >= 1
      ) {
        if (
          moment(new Date(Date.now())).format("YYYY") >=
            moment(el.createdDate).format("YYYY") &&
          moment(new Date(Date.now())).format("M") >=
            moment(el.createdDate).format("M") &&
          moment(new Date(Date.now())).diff(el.createdDate, "days") >= 1
        ) {
          const uri = `https://api.revmeup.in/api/v1/chatbot?Day=${moment(
            new Date(Date.now())
          ).diff(el.createdDate, "days")}`;
          const DATA = await fetch(uri, {
            method: "get",
            Accept: "application/json",
            headers: {
              Authorization: "Bearer " + tokenData.token,
            },
          }).then((res) => res.json());
          console.log(DATA[0]);
          try {
            const chat = await Chat.create({
              sender: el.senderId,
              receiver: el.receiverId,
              roomId: el.roomId,
              message: DATA[0].Message,
              isRating: DATA[0].IsRating,
              isRadio: DATA[0].isRadio,
              isText: DATA[0].isText,
              isStoreRating: DATA[0].isStoreRating,
              questionId: DATA[0].MessageId,
              time: moment.utc(new Date(Date.now())).format(),
            });
            console.log(chat);

            const getProductURL = `https://apistaging.revmeup.in/api/v1/product?product_id=`+el.senderId;
                const productData = await fetch(URL, {
                  method: "get",
                  Accept: "application/json",
                  headers: {
                    Authorization: "Bearer " + tokenData.token,
                  },
                }).then((res) => res.json());
                console.log(productData);
            let msg = {
                            message: productData.product_name + " messaged you",
                            notifier_user_id: el.senderId,
                            user_id: el.receiverId,
                            Type: "Product",
                            typeId: el.senderId,
                            timestamp: Date().toString()
                        }
                        console.log('msg' + JSON.stringify(msg));

                        // message insertion in firebase : location = db.ref('messages/' + req.params.userid);
                        let newKey = (await db.ref('messages/' + el.receiverId).push()).key;
                        let update = {};
                        update["messages/" + el.receiverId + '/' + newKey] = msg;
                        db.ref().update(update);
                        ///

            await ChatRoom.findByIdAndUpdate(el._id, {
              checkeddate: `${moment.utc(new Date(Date.now())).format()}`,
              modifieddate: `${moment.utc(new Date(Date.now())).format()}`
            });
          } catch (e) {
            console.log(e.message);
          }
        } else console.log("No data found");
      }
      }catch(err){
        console.log(err.message);
      }
    });
  } catch (e) {
    console.log(e.message);
  }
}
getData();

// console.log(moment.utc("2020-08-26T12:11:08Z").format("llll"));
// if (
// const a = "2020-09-01T20:52:57+05:30";
//const b = moment(new Date(Date.now())).diff(a, "days");
//console.log(b);
//  const b = moment(new Date(Date.now())).subtract(1, "days").format();
//   console.log(b);
// ) {
//   console.log(true);
// } else console.log(false);
// const a = moment("2020-08-13T20:51:30.000+00:00")
//   .add(1, "d")
//   .format("dddd, MMMM Do YYYY");
// console.log(a);

// const b = moment(new Date(Date.now())).format("dddd, MMMM Do YYYY");
// console.log(b);
