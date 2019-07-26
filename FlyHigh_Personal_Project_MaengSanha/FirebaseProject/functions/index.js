/* jshint esversion: 8 */

// Import Admin SDK
const admin = require('firebase-admin');
const functions = require('firebase-functions');
admin.initializeApp();

// get Database from Firestore
var db = admin.firestore();


// Create and Deploy Your First Cloud Functions
// https://firebase.google.com/docs/functions/write-firebase-functions

// exports.helloFirebase = functions.https.onRequest((request, response) => {
//     res = {
//         'text': "Hello from Firebase!",
//         'responseType': 'ephemeral'
//     };
//     response.send(res);
// });


// command: /lib
exports.lib = functions.https.onRequest((request, response) => {
    // create default response query
    var res = {
        /*  ephemeral: only I can see this message
            inChannel : everyone can see this message */
        'responseType': 'ephemeral',
        'text': "도서 목록 가져왔어요, 왈!\n\n"
    };
    db.collection('BookList').get().then((snapshot) => {
        snapshot.forEach((doc) => {
            // not to show DEFAULT data on response query
            if (doc.data().book_title !== 'DEFAULT'){
                res.text += doc.data().book_title + ' / ' + doc.data().office + '\n';
            }
        });
        // send response qeury to Dooray! Messenger
        // Success: status code 200
        response.send(res);
        // return Promise
        return;
    }).catch((err) => {
        // if Error occurs, go to Firebase\functions\log
        console.log("Error getting documents", err);
    });
});


// command: /bookadd book_title, author, publisher, category, purchase_date, office, borrower
exports.bookadd = functions.https.onRequest((request, response) => {
    // get command param, split by commas
    var query = request.body.text.split(',', 7);
    // remove spaces
    for (var info in query){
        info.trim();
    }
    // create response query
    var res = {
        /*  ephemeral: only I can see this message
            inChannel : everyone can see this message */
        'responseType': 'ephemeral',
        'text': "도서 목록에 " + query[0] + "(을)를 추가했습니다."
    };
    // set data to Database
    db.collection('BookList').doc().set({
        'book_title': query[0],
        'author': query[1],
        'publisher': query[2],
        'category': query[3],
        'purchase_date': query[4],
        'office': query[5],
        'borrower': query[6]
    });
    // send response query to Dooray! Messenger
    // Success: status code 200
    response.send(res);
});


// command: /booksearch book_title
exports.booksearch = functions.https.onRequest((request, response) => {
    // get command param, remove spaces
    var title = request.body.text.trim();
    // create default response query
    var res = {
        /*  ephemeral: only I can see this message
            inChannel : everyone can see this message */
        'responseType': 'ephemeral',
        'text': "해당 도서가 존재하지 않아요, 왈!"
    };
    db.collection('BookList').get().then((snapshot) => {
        snapshot.forEach((doc) => {
            var data = doc.data();
            if (data.book_title === title){
                // if book is not on loan
                if (data.borrower === ''){
                    res.text = title + '(은)는 ' + data.office + "에 있어요.\n지금 대여 가능합니다, 왈!";
                    response.send(res);
                }
                // if book is on loan
                else{
                    res.text = title + '(은)는 ' + data.office + "에 있어요.\n현재 대여중입니다.\n" + "대여자는 " + data.borrower + '님입니다.';
                    response.send(res);
                }
            }
        });
        // send response query to Dooray! Messenger
        // Success: status code 200
        response.send(res);
        // return Promise
        return;
    }).catch((err) => {
        // if Error occurs, go to Firebase\functions\log
        console.log("Error getting documents", err);
    });
});

// command: /req book_title, author, publisher, applicant, office, url
exports.bookreq = functions.https.onRequest((request, response) => {
    // get command param, split by commas
    var query = request.body.text.split(',', 6);
    for (var info in query){
        // remove spaces
        info.trim();
    }
    var data = {
        'book_title': query[0],
        'author': query[1],
        'publisher': query[2],
        'applicant': query[3],
        'office': query[4],
        'url': query[5],
        'is_purchased': false
    };
    // set data on Database
    db.collection('RequiredBooks').doc().set(data);
    // create response query
    var res = {
        /*  ephemeral: only I can see this message
            inChannel : everyone can see this message */
        'responseType': 'ephemeral',
        'text': data.applicant + "님, " + data.book_title + "(이)가 신청됐어요, 왈!"
    };
    // send response query to Dooray! Messenger
    // Success: status code 200
    response.send(res);
});


// command: /borrowable
exports.borrowable = functions.https.onRequest((request, response) => {
    // create default response query
    var res = {
        /*  ephemeral: only I can see this message
            inChannel : everyone can see this message */
        'responseType': 'ephemeral',
        'text': "대여 가능한 도서 목록은 여기 있어요, 왈!\n\n"
    };
    db.collection('BookList').get().then((snapshot) => {
        snapshot.forEach((doc) => {
            var data = doc.data();
            // not to show DEFAULT data on response query
            if (data.borrower === '' && data.book_title!=='DEFAULT'){
                res.text += data.book_title + '\n';
            } 
        });
        // send response query to Dooray! Messenger
        // Success: status code 200
        response.send(res);
        // return Promise
        return;
    }).catch((err) => {
        // if Error occurs, go to Firebase\functions\log
        console.log("Error getting documents", err);
    });
});


// command: /delreqbook book_title
exports.delreqbook = functions.https.onRequest((request, response) => {
    // get command param, remove spaces
    var title = request.body.text.trim();
    // create response query
    var res = {
        /*  ephemeral: only I can see this message
            inChannel : everyone can see this message */
        'responseType': 'ephemeral',
        'text': "도서 신청 목록에서 " + title + "(을)를 삭제했습니다."
    };
    db.collection('RequiredBooks').get().then((snapshot) => {
        snapshot.forEach((doc) => {
            var data = doc.data();
            if (data.book_title===title){
                // delete data from Database
                db.collection('RequiredBooks').doc(doc.id).delete();
                // send response query to Dooray! Messenger
                // Success: status code 200
                response.send(res);
            }
        });
        // return Promise
        return;
    }).catch((err) => {
        // if Error occurs, go to Firebase\functions\log
        console.log("Error getting documents", err);
    });
});


// command: /bookdel book_title
exports.bookdel = functions.https.onRequest((request, response) => {
    // get command param, remove spaces
    var title = request.body.text.trim();
    // create response query
    var res = {
        /*  ephemeral: only I can see this message
            inChannel : everyone can see this message */
        'responseType': 'ephemeral',
        'text': "도서 목록에서 " + title + "(을)를 삭제했습니다."
    };
    db.collection('BookList').get().then((snapshot) => {
        snapshot.forEach((doc) => {
            var data = doc.data();
            if (data.book_title===title){
                // delete data from Database
                db.collection('BookList').doc(doc.id).delete();
                // send response query to Dooray! Messenger
                // Success: status code 200
                response.send(res);
            }
        });
        // return Promise
        return;
    }).catch((err) => {
        // if Error occurs, go to Firebase\functions\log
        console.log("Error getting documents", err);
    });
});


// // command: /bookedit book_title, author, publisher, category, purchase_date, office, borrower
// exports.bookedit = functions.https.onRequest((request, response) => {
//     var parsed_data = request.body.text.split(',', 7);
//     for (var info in parsed_data){
//         info.trim();
//     }
//     var target = parsed_data[0];
//     var res = {
//         'responseType': 'ephemeral',
//         'text': "도서 목록에서 " + target + "의 도서 정보가 수정되었습니다."
//     };
//     db.collection('BookList').get().then((snapshot) => {
//         snapshot.forEach((doc) => {
//             var data = doc.data();
//             if (data.book_title===target){
//                 db.collection('BookList').doc(doc.id).set({
//                     'book_title': parsed_data[0],
//                     'author': parsed_data[1],
//                     'publisher': parsed_data[2],
//                     'category': parsed_data[3],
//                     'purchase_date': parsed_data[4],
//                     'office': parsed_data[5],
//                     'borrower': parsed_data[6]
//                 });
//             }
//         });
//         response.send(res);
//         return;
//     }).catch((err) => {
//         console.log("Error getting documents", err);
//     });
// });


// command: /reqList
exports.reqList = functions.https.onRequest((request, response) => {
    // create default reponse query
    var res = {
        /*  ephemeral: only I can see this message
            inChannel : everyone can see this message */
        'responseType': 'ephemeral',
        'text': "현재 도서 신청 현황입니다.\n\n"
    };
    db.collection('RequiredBooks').get().then((snapshot) => {
        snapshot.forEach((doc) => {
            // not to show DEFAULT data on response query
            if (doc.data().book_title!=='DEFAULT'){
                res.text += '도서명: ' + doc.data().book_title + '\nurl: ' + doc.data().url;
                res.text += '\n신청자: ' + doc.data().applicant + '\n구매여부: ' + doc.data().is_purchased + '\n\n';
            }
        });
        // send response query to Dooray! Messenger
        // Success: status code 200
        response.send(res);
        // return Promise
        return;
    }).catch((err) => {
        // if Error occurs, go to Firebase\functions\log
        console.log("Error getting documents", err);
    });
});


// command: /borrow book_title, user_name
exports.borrow = functions.https.onRequest((request, response) => {
    // get command param, split by commas
    var query = request.body.text.split(',', 2);
    // access by index, remove spaces
    var title = query[0].trim();
    var user_name = query[1].trim();
    // create default response query
    var res = {
        /*  ephemeral: only I can see this message
            inChannel : everyone can see this message */
        'responseType': 'ephemeral',
        'text': title + "이 도서 목록에 없어요\n도서를 신청하시려면 /req를 이용해주세요, 왈!"
    };
    db.collection('BookList').get().then((snapshot) => {
        snapshot.forEach((doc) => {
            if (doc.data().book_title===title){
                if (doc.data().borrower===''){
                    // set data to Database
                    db.collection('BookList').doc(doc.id).set({
                        'book_title': title,
                        'author': doc.data().author,
                        'publisher': doc.data().publisher,
                        'category': doc.data().category,
                        'purchase_date': doc.data().purchase_date,
                        'office': doc.data().office,
                        'borrower': user_name
                    });
                    res.text = title + "(이)가 대출됐어요, 왈!";
                }
                else{
                    // if someone already borrows, notifies it
                    res.text = title + "(이)가 이미 대출 중이예요.\n대여자는 " + doc.data().borrower + "님입니다, 왈!";
                }
            }
        });
        // send response query to Dooray! Messenger
        // Success: status code 200
        response.send(res);
        // return Promise
        return;
    }).catch((err) => {
        // if Error occurs, go to Firebase\functions\log
        console.log("Error getting documents", err);
    });
});


// command: /return book_title
exports.bookreturn = functions.https.onRequest((request, response) => {
    // create default response query
    var res = {
        /*  ephemeral: only I can see this message
            inChannel : everyone can see this message */
        'responseType': 'ephemeral',
        'text': "해당 도서는 현재 대여 중이 아니다옹~"
    };
    // get command param, remove spaces
    var title = request.body.text.trim();
    db.collection('BookList').get().then((snapshot) => {
        snapshot.forEach((doc) => {
            if (doc.data().book_title===title){
                // updates data info
                db.collection('BookList').doc(doc.id).set({
                    'book_title': title,
                    'author': doc.data().author,
                    'publisher': doc.data().publisher,
                    'category': doc.data().category,
                    'purchase_date': doc.data().purchase_date,
                    'office': doc.data().office,
                    'borrower': ''
                });
                // modify response text
                res.text = title + "(을)를 반납했다옹~";
            }
        });
        // send response query to Dooray! Messenger
        // Success: status code 200
        response.send(res);
        // return Promise
        return;
    }).catch((err) => {
        // if Error occurs, go to Firebase\functions\log
        console.log("Error getting documents", err);
    });
});