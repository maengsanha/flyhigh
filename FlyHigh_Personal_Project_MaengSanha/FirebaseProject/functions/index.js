// The Cloud Functions for Firebase SDK to create Cloud Functions and setup triggers.
const functions = require('firebase-functions');

// The Firebase Admin SDK to access the Firebase Realtime Database.
// Import Admin SDK
const admin = require('firebase-admin');
admin.initializeApp();
  
// get Database::FlyHigh Library from Firebase-Firestore
const db = admin.firestore();

// Create and Deploy Your First Cloud Functions
// https://firebase.google.com/docs/functions/write-firebase-functions


exports.helloFirebase = functions.https.onRequest((request, response) => {
  res = {"text" : "Hello from Firebase! 왈!", "responseType" : "inChannel"};
  response.send(res); 
});


exports.bookList = functions.https.onRequest((request, response) => {
    var library = db.collection('Book List').doc('Books');
    var getBooks = library.get().then(doc => {
        if (!doc.exists) {
            console.log('No such document!');
        } else {
            // console.log(doc.data());
            res = {
              "text" : "도서 목록 가져왔어요. 왈!\nhttps://us-central1-flyhigh-library.cloudfunctions.net/bookList",
              "Book List" : doc.data(),
              "responseType" : "ephemeral"
              };
            response.send(res);
        }
        return
    }).catch(err => {
        console.log('Error getting document : ', err);
    });
});