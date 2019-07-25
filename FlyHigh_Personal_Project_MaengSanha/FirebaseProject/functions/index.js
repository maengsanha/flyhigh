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


exports.bookList = functions.https.onRequest((request, response) => {
    var res = {
        'responseType': 'ephemeral',
        'text': "도서 목록 가져왔어요, 왈!\n\n"
    };
    db.collection('BookList').get().then((snapshot) => {
        snapshot.forEach((doc) => {
            console.log(doc.id, '=>', doc.data());
            res.text += doc.data().book_title + ' / ' + doc.data().office + '\n';
        });
        response.send(res);
        return;
    }).catch((err) => {
        console.log("Error getting documents", err);
    });
});


exports.addBook = functions.https.onRequest((request, response) => {
    var parsed_data = request.body.text.split(',', 7);
    for (var info in parsed_data){
        info.trim();
    }
    var data = {
        'book_title': parsed_data[0],
        'author': parsed_data[1],
        'publisher': parsed_data[2],
        'category': parsed_data[3],
        'purchase_date': parsed_data[4],
        'office': parsed_data[5],
        'lender': parsed_data[6]
    };
    var res = {
        'responseType': 'ephemeral',
        'text': "도서 목록에 " + parsed_data[0] + "(을)를 추가했습니다."
    };
    var setBook = db.collection('BookList').doc().set(data);
    response.send(res);
});


exports.findBook = functions.https.onRequest((request, response) => {
    var target = request.body.text.trim();
    var res = {
        'responseType': 'ephemeral',
        'text': "해당 도서가 존재하지 않아요, 왈!"
    };
    db.collection('BookList').get().then((snapshot) => {
        snapshot.forEach((doc) => {
            var data = doc.data();
            if (data.book_title===target){
                if (data.lender===''){
                    res.text = target + '(은)는 ' + data.office + "에 있어요.\n지금 대여 가능합니다, 왈!";
                    response.send(res);
                }
                else{
                    res.text = target + '(은)는 ' + data.office + "에 있어요.\n현재 대여중입니다.\n" + "대여자는 " + data.lender + '님입니다.';
                    response.send(res);
                }
            }
        });
        response.send(res);
        return;
    }).catch((err) => {
        console.log("Error getting documents", err);
    });
});


exports.applyBook = functions.https.onRequest((request, response) => {
    var res = {
        'responseType': 'ephemeral',
        'text': "도서가 신청됐어요, 왈!"
    };
    var parsed_data = request.body.text.split(',', 4);
    for (var info in parsed_data){
        info.trim();
    }
    var data = {
        'book_title': parsed_data[0],
        'author': parsed_data[1],
        'publisher': parsed_data[2],
        'office': parsed_data[3],
    };
    db.collection('AppliedBooks').doc().set(data);
    response.send(res);
});


exports.canLoan = functions.https.onRequest((request, response) => {
    var res = {
        'responseType': 'ephemeral',
        'text': "대여 가능한 도서 목록은 여기 있어요, 왈!\n\n"
    };
    db.collection('BookList').get().then((snapshot) => {
        snapshot.forEach((doc) => {
            var data = doc.data();
            if (data.lender===''){
                res.text += data.book_title + '\n';
            } 
        });
        response.send(res);
        return;
    }).catch((err) => {
        console.log("Error getting documents", err);
    });
});


exports.deleteAppliedBook = functions.https.onRequest((request, response) => {
    var target = request.body.text.trim();
    var res = {
        'responseType': 'ephemeral',
        'text': "도서 신청 목록에서 " + target + "(을)를 삭제했습니다."
    };
    db.collection('AppliedBooks').get().then((snapshot) => {
        snapshot.forEach((doc) => {
            var data = doc.data();
            if (data.book_title===target){
                db.collection('AppliedBooks').doc(doc.id).delete();
                response.send(res);
            }
        });
        return;
    }).catch((err) => {
        console.log("Error getting documents", err);
    });
});


exports.deleteBook = functions.https.onRequest((request, response) => {
    var target = request.body.text.trim();
    var res = {
        'responseType': 'ephemeral',
        'text': "도서 목록에서 " + target + "(을)를 삭제했습니다."
    };
    db.collection('BookList').get().then((snapshot) => {
        snapshot.forEach((doc) => {
            var data = doc.data();
            if (data.book_title===target){
                var deleter = db.collection('BookList').doc(doc.id).delete();
                response.send(res);
            }
        });
        return;
    }).catch((err) => {
        console.log("Error getting documents", err);
    });
});


exports.editBook = functions.https.onRequest((request, response) => {
    var parsed_data = request.body.text.split(',', 7);
    for (var info in parsed_data){
        info.trim();
    }
    var target = parsed_data[0];
    var res = {
        'responseType': 'ephemeral',
        'text': "도서 목록에서 " + target + "의 도서 정보가 수정되었습니다."
    };
    db.collection('BookList').get().then((snapshot) => {
        snapshot.forEach((doc) => {
            var data = doc.data();
            if (data.book_title===target){
                db.collection('BookList').doc(doc.id).set({
                    'book_title': parsed_data[0],
                    'author': parsed_data[1],
                    'publisher': parsed_data[2],
                    'category': parsed_data[3],
                    'purchase_date': parsed_data[4],
                    'office': parsed_data[5],
                    'lender': parsed_data[6]
                });
            }
        });
        response.send(res);
        return;
    }).catch((err) => {
        console.log("Error getting documents", err);
    });
});


exports.appliedBooks = functions.https.onRequest((request, response) => {
    var res = {
        'responseType': 'ephemeral',
        'text': "현재 도서 신청 현황입니다.\n\n"
    };
    db.collection('AppliedBooks').get().then((snapshot) => {
        snapshot.forEach((doc) => {
            res.text += doc.data().book_title + '\n';
        });
        response.send(res);
        return;
    }).catch((err) => {
        console.log("Error getting documents", err);
    });
});


exports.loanBook = functions.https.onRequest((request, response) => {
    var parsed_data = request.body.text.split(',', 2);
    var target = parsed_data[0].trim();
    var user_name = parsed_data[1].trim();
    var res = {
        'responseType': 'ephemeral',
        'text': target + "이 도서 목록에 없어요\n도서를 신청하시려면 /applyBook을 이용해주세요, 왈!"
    };
    db.collection('BookList').get().then((snapshot) => {
        snapshot.forEach((doc) => {
            if (doc.data().book_title===target){
                if (doc.data().lender===''){
                    db.collection('BookList').doc(doc.id).set({
                        'book_title': target,
                        'author': doc.data().author,
                        'publisher': doc.data().publisher,
                        'category': doc.data().category,
                        'purchase_date': doc.data().purchase_date,
                        'office': doc.data().office,
                        'lender': user_name
                    });
                    res.text = target + "(이)가 대출되었어요, 왈!";
                }
                else{
                    res.text = target + "(이)가 이미 대출 중입니다.\n대여자는 " + doc.data().lender + "님입니다.";
                }
            }
        });
        response.send(res);
        return;
    }).catch((err) => {
        console.log("Error getting documents", err);
    });
});