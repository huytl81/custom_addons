// if ('serviceWorker' in navigator && 'PushManager' in window) {
//     navigator.serviceWorker.register('/static/src/js/service_worker.js')
//     .then(function(swReg) {
//         console.log('Service Worker is registered', swReg);

//         swReg.pushManager.getSubscription()
//         .then(function(subscription) {
//             if (subscription === null) {
//                 // Ask user to subscribe
//                 subscribeUser(swReg);
//             } else {
//                 console.log('User is already subscribed');
//             }
//         });
//     })
//     .catch(function(error) {
//         console.error('Service Worker Error', error);
//     });
// }

// function subscribeUser(swReg) {
//     const applicationServerKey = urlB64ToUint8Array('YOUR_PUBLIC_VAPID_KEY');
//     swReg.pushManager.subscribe({
//         userVisibleOnly: true,
//         applicationServerKey: applicationServerKey
//     })
//     .then(function(subscription) {
//         console.log('User is subscribed:', subscription);
//         // Send subscription to server
//         sendSubscriptionToServer(subscription);
//     })
//     .catch(function(error) {
//         console.error('Failed to subscribe the user: ', error);
//     });
// }

// function urlB64ToUint8Array(base64String) {
//     const padding = '='.repeat((4 - base64String.length % 4) % 4);
//     const base64 = (base64String + padding)
//         .replace(/\-/g, '+')
//         .replace(/_/g, '/');

//     const rawData = window.atob(base64);
//     const outputArray = new Uint8Array(rawData.length);

//     for (let i = 0; i < rawData.length; ++i) {
//         outputArray[i] = rawData.charCodeAt(i);
//     }
//     return outputArray;
// }

// function sendSubscriptionToServer(subscription) {
//     // Send subscription to your server
//     fetch('/save-subscription', {
//         method: 'POST',
//         body: JSON.stringify(subscription),
//         headers: {
//             'Content-Type': 'application/json'
//         }
//     });
// }