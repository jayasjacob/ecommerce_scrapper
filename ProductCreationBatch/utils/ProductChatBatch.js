const fetch = require("node-fetch");
const moment = require("moment");
const mongoose = require("mongoose");
const dotenv = require("dotenv");
const admin = require('firebase-admin');
const serviceAccount = require('./ServiceAccountKey.json');

dotenv.config({ path: "./config.env" });

// const DB = process.env.DATABASE.replace(
//   "<PASSWORD>",
//   process.env.DATABASE_PASSWORD
// );

 admin.initializeApp({
     credential: admin.credential.cert(serviceAccount),
     databaseURL: "https://revitup-86a41.firebaseio.com"
 });

 const firebasedb = admin.database();

// mongoose
//   .connect(DB, {
//     useNewUrlParser: true,
//     useCreateIndex: true,
//     useFindAndModify: true,
//     useUnifiedTopology: true,
//   })
//   .then(() => {
//     console.log("DB connection successful");
//   });
async function getData() {
  try {
    const body = {
      userid: process.env.TOKEN_LOGIN_USERNAME,
      password: process.env.TOKEN_LOGIN_PASSWORD,
    };
    const pri = process.env.BASE_URL+"/user/login";
    const tokenData = await fetch(pri, {
      method: "POST",
      body: JSON.stringify(body),
      headers: { "Content-Type": "application/json" },
    }).then((res) => res.json());

    console.log('token : ' + tokenData.token);
    const URL = process.env.BASE_URL+"/ChatRoom?senderId=product";
    const data = await fetch(URL, {
      method: "get",
      Accept: "application/json",
      headers: {
        Authorization: "Bearer " + tokenData.token,
      },
    }).then((res) => res.json());

    data.forEach(async (el) => {
      try{
        if (el.checkeddate == undefined ||
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
  //         console.log('data' + JSON.stringify(el));
  // console.log('date' + new Date(Date.now()));
  // console.log('checkeddate : ' + el.checkeddate);
  // console.log('difference' + moment(new Date(Date.now())).diff(el.createdDate, "days"));

          const uri = process.env.BASE_URL+`/chatbot?Day=${moment(
            new Date(Date.now())
          ).diff(el.createdDate, "days")}`;
                console.log('chatbotUri : ' + uri);
          const chatbotMessage = await fetch(uri, {
            method: "get",
            Accept: "application/json",
            headers: {
              Authorization: "Bearer " + tokenData.token,
            },
          }).then((res) => res.json());
          console.log('chatbot' + chatbotMessage);
          try {
            if(chatbotMessage.length > 0){

              chatbotMessage.forEach(async (message) => {
                const productChatBody = {
                  sender: el.senderId,
                    receiver: el.receiverId,
                    roomId: el.roomId,
                    message: message.Message,
                    seen: false,
                    type: 'question',
                    questionId: message.MessageId,
                    time: moment.utc(new Date(Date.now())).format(),
                    options: message.options
                };

                const createProductChatUri = process.env.BASE_URL+'/productChat';
                const productChatResponse = await fetch(createProductChatUri, {
                  method: "POST",
                  body: JSON.stringify(productChatBody),
                  headers: { "Content-Type": "application/json", Authorization: "Bearer " + tokenData.token },
                }).then((res) => res.json());

                var productId = el.senderId.replace('product','');
                const getProductURL = process.env.BASE_URL+`/product?product_id=`+productId;
                    const productData = await fetch(getProductURL, {
                      method: "get",
                      Accept: "application/json",
                      headers: {
                        Authorization: "Bearer " + tokenData.token,
                      },
                    }).then((res) => res.json());

                var currentTime = new Date();
var currentOffset = currentTime.getTimezoneOffset();
var ISTOffset = 330;   // IST offset UTC +5:30
var ISTTime = new Date(currentTime.getTime() + (ISTOffset + currentOffset)*60000);

                  const updateChatRoomObj = {
                  checkeddate: ISTTime.toISOString(),
                  modifieddate: ISTTime.toISOString()
                };

                const updateChatRoomURL = process.env.BASE_URL+'/ChatRoom/' + el.roomId + '/' + el.senderId;
                console.log('chatroomurl : ' + JSON.stringify(updateChatRoomObj));
                const updateChatRoom = await fetch(updateChatRoomURL, {
                  method: "PATCH",
                  body: JSON.stringify(updateChatRoomObj),
                  headers: {
                        "Content-Type": "application/json",
                    Authorization: "Bearer " + tokenData.token,
                  },
                }).then((res) => res.json());
                console.log('updateChatRoom : ' + JSON.stringify(updateChatRoom));

                const modifyChatRoomURL = process.env.BASE_URL+'/ChatRoom/' + el.roomId;
                const modifyChatRoom = await fetch(modifyChatRoomURL, {
                  method: "PATCH",
                  body: JSON.stringify(updateChatRoomObj),
                  headers: {
                        "Content-Type": "application/json",
                    Authorization: "Bearer " + tokenData.token,
                  },
                }).then((res) => res.json());


                if(productData.length > 0){
                    console.log('productData : ' + productData[0].product_id + '***' + productData[0].product_name);

                    let msg = {
                                message: productData[0].product_name + " messaged you",
                                notifier_user_id: el.senderId,
                                user_id: el.receiverId,
                                Type: "Product",
                                typeId: el.senderId,
                                timestamp: Date().toString()
                            }
                            console.log('msg' + JSON.stringify(msg));

                      // message insertion in firebase : location = db.ref('messages/' + req.params.userid);
                      let newKey = (await firebasedb.ref('messages/' + el.receiverId).push()).key;
                      let update = {};
                      update["messages/" + el.receiverId + '/' + newKey] = msg;
                      firebasedb.ref().update(update);
                      ///

                    //   await ChatRoom.findByIdAndUpdate(el._id, {
                    //   checkeddate: `${moment.utc(new Date(Date.now())).format()}`,
                    // });
                  }

              });
            }
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
