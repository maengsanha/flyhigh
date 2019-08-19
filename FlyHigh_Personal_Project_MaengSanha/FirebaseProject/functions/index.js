// jshint esversion: 8
// Runtime: Node.js 8
// firebase --version: 7.2.2

// import admin SDK
const admin = require('firebase-admin');
const functions = require('firebase-functions');
admin.initializeApp();

// import string-similarity library
const stringSimilarity = require('string-similarity');

// get Database from Firestore
const db = admin.firestore();

/*********************************************************************************/
/*// Create and Deploy Your First Cloud Functions                                */
/*// https://firebase.google.com/docs/functions/write-firebase-functions         */
/*                                                                               */
/*// command: /hello                                                             */
/*exports.helloFirebase = functions.https.onRequest((request, response) => {     */
/*    // create response query                                                   */
/*    var res = {                                                                */
/*        'responseType': 'ephemeral',                                           */
/*        'text': "Hello from Firebase!"                                         */
/*    };                                                                         */
/*    // send response query to Dooray! Messenger                                */
/*    // Success -> status code: 200                                             */
/*    response.send(res);                                                        */
/*});                                                                            */
/*********************************************************************************/

// ------------------------------------------------------------------------------- User Command -------------------------------------------------------------------------------

// // command: /lib
// exports.lib = functions.https.onRequest((request, response) => {
//     // create default response query
//     var res = {
//         /*
//         ephemeral: only I can see this message
//         inChannel : everyone can see this message
//         */
//         'responseType': 'ephemeral',
//         'text': "도서 목록 가져왔어요, 왈!\n\n"
//     };
//     db.collection('BookList').get().then((snapshot) => {
//         snapshot.forEach((doc) => {
//             // not to show DEFAULT data on response query
//             if (doc.data().book_title !== 'DEFAULT'){
//                 res.text += doc.data().book_title + ' / ' + doc.data().office + '\n';
//             }
//         }); // end forEach
//         // send response qeury to Dooray! Messenger
//         // Success -> status code: 200
//         response.send(res);
//         // return Promise
//         return;
//     }).catch((err) => {
//         // if Error occurs, go to Firebase\functions\log
//         console.log("Error getting documents", err);
//     }); // end then
// }); // end lib


// command: /lib
exports.lib = functions.https.onRequest((request, response) => {
    // create response query with button attachments
    var res = {
        // ephemeral: only I can see this message
        // inChannel : everyone can see this message
        // default: ephemeral
        'responseType': 'ephemeral',
        'text': "도서 목록 가져왔어요, 왈!",
        'attachments': [
            {
                'callbackId': "flyhigh-library"
            }
        ] // end attachments
    }; // end res
    db.collection('BookList').get().then((snapshot) => {
        snapshot.forEach((doc) => {
            var data = doc.data();
            var title = data.book_title;
            if (title!=='DEFAULT')
            {
                var field = {
                    'fields': [
                        {
                            'title': title,
                            'value': '',
                            'short': true
                        }
                    ]
                };
                var action = {
                    'actions': [
                        {
                            'type': 'button',
                            'text': '대여하기',
                            'name': title,
                            'value': 'btnValue'
                        }
                    ]
                };
                if (data.borrower_email!=='')
                    action.actions[0].text = '대여 중';
                res.attachments.push(field, action);
            }
        }); // end forEach
        // send response query to Dooray! Messenger
        // Success -> status code: 200
        response.send(res);
        return;    // return Promise
    }).catch((err) => {
        console.log("Error getting documents", err);    // if Error occurs, go to Firebase\functions\log
    }); // end then
}); // end lib


exports.borrow = functions.https.onRequest((request, response) => {
    // get data from request query
    var borrower_email = request.body.user.email;
    var title = request.body.actionName;
    // create default response query
    var res = {
        // ephemeral: only I can see this message
        // inChannel : everyone can see this message
        // default: ephemeral
        'responseType': 'ephemeral',
        'deleteOriginal': true,
        'text': 'DEFAULT'
    };
    db.collection('BookList').get().then((snapshot) => {
        snapshot.forEach((doc) => {
            var data = doc.data();
            if (data.book_title===title)
            {
                if (data.borrower_email!=='')
                    res.text = "해당 도서는 현재 대여 중이예요, 대여자는 " + data.borrower_email + "님입니다, 왈!";
                else
                {
                    db.collection('BookList').doc(doc.id).update({'borrower_email': borrower_email});   // update data
                    res.text = "도서 대여가 완료됐어요, 왈!";
                }
                // send response query to Dooray! Messenger
                // Success -> status code: 200
                response.send(res);
            }
        }); // end forEach
        return;    // return Promise
    }).catch((err) => {
        console.log("Error getting documnets", err);    // if Error occurs, go to Firebase\functions\log
    }); // end then
}); // end borrow


// command: /bookSearch key_word
exports.bookSearch = functions.https.onRequest((request, response) => {
    var key_word = request.body.text.replace(/\s/g,'');    // get command param, remove spaces

    // create default response query
    var res = {
        // ephemeral: only I can see this message
        // inChannel : everyone can see this message
        // default: ephemeral
        'responseType': 'ephemeral',
        'text': ''
    };
    db.collection('BookList').get().then((snapshot) => {
        snapshot.forEach((doc) => {
            var data = doc.data();
            var _title = data.book_title.replace(/\s/g,'');
            var similarity = stringSimilarity.compareTwoStrings(key_word, _title);    // compare two titles' similarity
            if (similarity!==0)    // if two titles are related
            {
                if (data.borrower_email === '')    // if book is not on loan
                    res.text += data.book_title + '(은)는 ' + data.office + "에 있어요.\n지금 대여 가능합니다, 왈!\n";
                else    // if book is on loan
                    res.text += data.book_title + '(은)는 ' + data.office + "에 있어요.\n현재 대여중입니다.\n" + '대여자는 ' + data.borrower_email + '님입니다, 왈!\n';
            }
        }); // end forEach
        if (res.text==='')
            res.text = "해당 키워드로 검색한 결과가 존재하지 않아요, 왈!";
        // send response query to Dooray! Messenger
        // Success -> status code: 200
        response.send(res);
        return;    // return Promise
    }).catch((err) => {
        console.log("Error getting documents", err);    // if Error occurs, go to Firebase\functions\log
    }); // end then
}); // end bookSearch


// command: /bookReq url
exports.bookReq = functions.https.onRequest((request, response) => {
    var applicant = request.body.userEmail;
    var url = request.body.text.trim();    // get command param, remove spaces
    var data = {
        'url': url,
        'applicant': applicant,
        'reqstat': '구매 신청 중'
    };
    db.collection('RequiredBooks').doc().set(data);    // set data on Database
    // create response query
    var res = {
        // ephemeral: only I can see this message
        // inChannel : everyone can see this message
        // default: ephemeral
        'responseType': 'ephemeral',
        'text': "도서 신청이 완료됐어요, 왈!"
    };
    // send response query to Dooray! Messenger
    // Success -> status code: 200
    response.send(res);
}); // end bookReq


// // command: /borrowable
// exports.borrowable = functions.https.onRequest((request, response) => {
//     // create default response query
//     var res = {
//         /*
//         ephemeral: only I can see this message
//         inChannel : everyone can see this message
//         */
//         'responseType': 'ephemeral',
//         'text': "대여 가능한 도서 목록이다옹~\n\n"
//     };
//     db.collection('BookList').get().then((snapshot) => {
//         snapshot.forEach((doc) => {
//             var data = doc.data();
//             // not to show DEFAULT data on response query
//             if (data.borrower === '' && data.book_title!=='DEFAULT'){
//                 res.text += data.book_title + '\n';
//             } 
//         }); // end forEach
//         // send response query to Dooray! Messenger
//         // Success -> status code: 200
//         response.send(res);
//         // return Promise
//         return;
//     }).catch((err) => {
//         // if Error occurs, go to Firebase\functions\log
//         console.log("Error getting documents", err);
//     }); // end then
// }); // end borrowable


// // command: /borrow book_title, user_name
// exports.borrow = functions.https.onRequest((request, response) => {
//     // get command param, split by commas
//     var query = request.body.text.split(',', 2);
//     // access by index, remove spaces
//     var title = query[0].trim();
//     var user_name = query[1].trim();
//     // create default response query
//     var res = {
//         /*
//         ephemeral: only I can see this message
//         inChannel : everyone can see this message
//         */
//         'responseType': 'ephemeral',
//         'text': title + "(이)가 도서 목록에 없다옹~\n도서를 신청하려면 /req를 이용해달라옹~"
//     };
//     db.collection('BookList').get().then((snapshot) => {
//         snapshot.forEach((doc) => {
//             if (doc.data().book_title===title){
//                 if (doc.data().borrower===''){
//                     // set data to Database
//                     db.collection('BookList').doc(doc.id).set({
//                         'book_title': title,
//                         'author': doc.data().author,
//                         'publisher': doc.data().publisher,
//                         'category': doc.data().category,
//                         'purchase_date': doc.data().purchase_date,
//                         'office': doc.data().office,
//                         'borrower': user_name
//                     });
//                     res.text = title + "(이)가 대출됐다옹~";
//                 }
//                 else{
//                     // if someone already borrows, notifies it
//                     res.text = title + "(이)가 이미 대출 중이다옹.\n대여자는 " + doc.data().borrower + "(이)다옹~";
//                 }
//             }
//         }); // end forEach
//         // send response query to Dooray! Messenger
//         // Success -> status code: 200
//         response.send(res);
//         // return Promise
//         return;
//     }).catch((err) => {
//         // if Error occurs, go to Firebase\functions\log
//         console.log("Error getting documents", err);
//     }); // end then
// }); // end borrow


// command: /bookReturn book_title
exports.bookReturn = functions.https.onRequest((request, response) => {
    // create default response query
    var res = {
        // ephemeral: only I can see this message
        // inChannel : everyone can see this message
        // default: ephemeral
        'responseType': 'ephemeral',
        'text': "해당 도서는 현재 대여 중이 아니예요, 왈!."
    };
    var title = request.body.text.trim();   // get command param, remove spaces
    db.collection('BookList').get().then((snapshot) => {
        snapshot.forEach((doc) => {
            if (doc.data().book_title.replace(/\s/g,'')===title.replace(/\s/g,''))
            {
                db.collection('BookList').doc(doc.id).update({    // updates data info
                    'borrower_email': ''
                });
                res.text = doc.data().book_title + "(을)를 반납했어요, 왈!.";   // update response text
            }
        }); // end forEach
        // send response query to Dooray! Messenger
        // Success -> status code: 200
        response.send(res);
        return;    // return Promise
    }).catch((err) => {
        console.log("Error getting documents", err);    // if Error occurs, go to Firebase\functions\log
    }); // end then
}); // end bookReturn

// ----------------------------------------------------------------------------------------- Admin Command -----------------------------------------------------------------------------------------

// command: /bookAdd book_title, author, publisher, category, purchase_date, office, borrower_email
exports.bookAdd = functions.https.onRequest((request, response) => {
    var query = request.body.text.split(',', 7);    // get command param, split by commas
    for (var info in query)
        info.trim();    // remove spaces
    // create response query
    var res = {
        // ephemeral: only I can see this message
        // inChannel : everyone can see this message
        // default: ephemeral
        'responseType': 'ephemeral',
        'text': "도서 목록에 " + query[0] + "(을)를 추가했습니다."
    };
    db.collection('BookList').doc().set({   // set data to Database
        'book_title': query[0],
        'author': query[1],
        'publisher': query[2],
        'category': query[3],
        'purchase_date': query[4],
        'office': query[5],
        'borrower_email': query[6]
    }); // end set
    // send response query to Dooray! Messenger
    // Success -> status code: 200
    response.send(res);
}); // end bookAdd


// command: /bookDel book_title
exports.bookDel = functions.https.onRequest((request, response) => {
    var title = request.body.text.trim();   // get command param, remove spaces
    // create response query
    var res = {
        // ephemeral: only I can see this message
        // inChannel : everyone can see this message
        // default: ephemeral
        'responseType': 'ephemeral',
        'text': "도서 목록에서 " + title + "(을)를 삭제했습니다."
    };
    db.collection('BookList').get().then((snapshot) => {
        snapshot.forEach((doc) => {
            var data = doc.data();
            if (data.book_title===title)
            {
                db.collection('BookList').doc(doc.id).delete();    // delete data from Database
                // send response query to Dooray! Messenger
                // Success -> status code: 200
                response.send(res);
            }
        });
        return;    // return Promise
    }).catch((err) => {
        console.log("Error getting documents", err);    // if Error occurs, go to Firebase\functions\log
    }); // end then
}); // end bookDel


// // command: /bookedit book_title, author, publisher, category, purchase_date, office, borrower
// exports.bookEdit = functions.https.onRequest((request, response) => {
//     // get command param, split by commas
//     var query = request.body.text.split(',', 7);
//     for (var info in query){
//         // remove spaces
//         info.trim();
//     }
//     var title = query[0];
//     // create reponse query
//     var res = {
//         /*
//         ephemeral: only I can see this message
//         inChannel : everyone can see this message
//         */
//         'responseType': 'ephemeral',
//         'text': "도서 목록에서 " + title + "의 도서 정보가 수정되었습니다."
//     };
//     db.collection('BookList').get().then((snapshot) => {
//         snapshot.forEach((doc) => {
//             var data = doc.data();
//             if (data.book_title===title){
//                 db.collection('BookList').doc(doc.id).set({
//                     // updates data
//                     'book_title': query[0],
//                     'author': query[1],
//                     'publisher': query[2],
//                     'category': query[3],
//                     'purchase_date': query[4],
//                     'office': query[5],
//                     'borrower': query[6]
//                 });
//             }
//         }); // end forEach
//         // send response query to Dooray! Messenger
//         // Success -> status code: 200
//         response.send(res);
//         // return Promise
//         return;
//     }).catch((err) => {
//         // if Error occurs, go to Firebase\functions\log
//         console.log("Error getting documents", err);
//     }); // end then
// }); // end bookEdit


// command: /reqList
exports.reqList = functions.https.onRequest((request, response) => {
    // create default reponse query
    var res = {
        // ephemeral: only I can see this message
        // inChannel : everyone can see this message
        // default: ephemeral
        'responseType': 'ephemeral',
        'text': "현재 도서 신청 현황입니다.\n\n"
    };
    db.collection('RequiredBooks').get().then((snapshot) => {
        snapshot.forEach((doc) => {
            if (doc.data().book_title!=='DEFAULT')    // not to show DEFAULT data on response query
                res.text += 'url: ' + doc.data().url + '\n신청자: ' + doc.data().applicant + '\n구매 신청 현황: ' + doc.data().reqstat + '\n\n';
        }); // end forEach
        // send response query to Dooray! Messenger
        // Success -> status code: 200
        response.send(res);
        return;    // return Promise
    }).catch((err) => {
        console.log("Error getting documents", err);    // if Error occurs, go to Firebase\functions\log
    }); // end then
}); // end reqList


// command: /reqDel book_title
exports.reqDel = functions.https.onRequest((request, response) => {
    var title = request.body.text.trim();   // get command param, remove spaces
    // create response query
    var res = {
        // ephemeral: only I can see this message
        // inChannel : everyone can see this message
        // default: ephemeral
        'responseType': 'ephemeral',
        'text': "도서 신청 목록에서 " + title + "(을)를 삭제했습니다."
    };
    db.collection('RequiredBooks').get().then((snapshot) => {
        snapshot.forEach((doc) => {
            var data = doc.data();
            if (data.book_title===title)
            {
                db.collection('RequiredBooks').doc(doc.id).delete();    // delete data from Database
                // send response query to Dooray! Messenger
                // Success -> status code: 200
                response.send(res);
            }
        }); // end forEach
        return;    // return Promise
    }).catch((err) => {
        console.log("Error getting documents", err);    // if Error occurs, go to Firebase\functions\log
    }); // end then
}); // end reqDel
