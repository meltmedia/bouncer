// Load the AWS SDK for Node.js
var AWS = require('aws-sdk');

/**
 * Don't hard-code your credentials!
 * Load them from disk or your environment instead.
 */
// AWS.config.update({accessKeyId: 'AKID', secretAccessKey: 'SECRET'});

// Instead, do this:
AWS.config.loadFromPath('./config/aws_credentials.json');

// Set your region for future requests.
AWS.config.update({region: 'us-east-1'});

// Create a bucket using bound parameters and put something in it.
// Make sure to change the bucket name from "myBucket" to something unique.
//var s3bucket = new AWS.S3({params: {Bucket: 'nodeTest'}});
//s3bucket.createBucket(function() {
//  var data = {Key: 'myKey', Body: 'Hello!'};
//  s3bucket.putObject(data, function(err, data) {
//    if (err) {
//      console.log("Error uploading data: ", err);
//    } else {
//      console.log("Successfully uploaded data to myBucket/myKey");
//    }
//  });
//});

var express = require('express'),
    app = express(),
    fs = require('fs'),
    bucketName = "nodeTest";

app.use(express.bodyParser());

//app.get('/files', function(req, res) {
//
//  function fileListMarkup(files) {
//    var markup = '<ul>\n';
//    files.forEach(function(file){
//      markup += '<li><a href="https://s3.amazonaws.com/'+bucketName+'/'+file.Key+'" target="_blank">'+file.Key+'</a></li>\n';
//    });
//    markup += '</ul>\n';
//    return markup;
//  }
//
//  var s3bucket = new AWS.S3({params: {Bucket: bucketName}});
//
//  res.setHeader('Content-Type', 'text/html');
//
//  s3bucket.listObjects({}, function(err, data) {
//    if (err) {
//      res.end("Error getting data: ", err);
//    } else {
//      res.end(fileListMarkup(data.Contents));
//    }
//  });
//
//});

app.get('/download/:filename', function(req, res) {

  var s3bucket = new AWS.S3({params: {Bucket: bucketName}});

  s3bucket.getObject({Key: req.params.filename}, function(err, data){
    if (err) {
      console.log(err);
      res.end("Error!");
    } else {
      console.log(data);
      res.setHeader('Content-Type', data.ContentType);
      res.end(data.Body);
    }
  });

  //res.redirect("https://s3.amazonaws.com/" + bucketName + "/" + req.params.filename);

});

app.get('/upload', function(req, res){
  var body = '<form method="post" enctype="multipart/form-data" action="/upload">' +
      '<input type="file" name="thumbnail">' +
      '<input type="submit">' +
      '</form>';
  res.setHeader('Content-Type', 'text/html');
  res.setHeader('Content-Length', body.length);
  res.end(body);

});

app.post('/upload', function(req, res, next) {

  // get the temporary location of the file
  var tmp_path = req.files.thumbnail.path;

//  // set where the file should actually exists - in this case it is in the "images" directory
//  var target_path = './uploads/' + req.files.thumbnail.name;
//
//  // move the file from the temporary location to the intended location
//  fs.rename(tmp_path, target_path, function(err) {
//    if (err) throw err;
//    // delete the temporary file, so that the explicitly set temporary upload dir does not get filled with unwanted files
//    fs.unlink(tmp_path, function() {
//      if (err) throw err;
//      res.send('File uploaded to: ' + target_path + ' - ' + req.files.thumbnail.size + ' bytes');
//    });
//  });

  var s3bucket = new AWS.S3({params: {Bucket: bucketName}});

  fs.readFile(tmp_path, function (err, data) {

    if (err) { throw err; }

    var dataToUpload = {
      Key: req.files.thumbnail.name,
      Body: data,
      ContentType: req.files.thumbnail.type
    };

    s3bucket.putObject(dataToUpload, function(err, data) {
      if (err) {
        console.log(err);
        res.end("Error uploading data");
      } else {
        res.end("Successfully uploaded data to https://s3.amazonaws.com/" + bucketName + "/" + req.files.thumbnail.name);
        fs.unlink(tmp_path, function() {
          if (err) throw err;
        });
      }
    });

  });

});

app.listen(3000);
console.log('Listening on port 3000');