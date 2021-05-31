exports.handler = (event, context, callback) => {
    var request = event.Records[0].cf.request;
    if ((request.uri != "") || (request.uri != "/")) {
          request.uri = "/secret";
        }
    return callback(null, request);
};
