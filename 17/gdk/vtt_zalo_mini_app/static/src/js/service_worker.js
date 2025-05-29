// // static/src/js/service-worker.js
// self.addEventListener('push', function(event) {
//     const options = event.data.json();
//     event.waitUntil(self.registration.showNotification(options.title, options));
// });

// self.addEventListener('notificationclick', function(event) {
//     event.notification.close();
//     event.waitUntil(clients.openWindow(event.notification.data.url));
// });