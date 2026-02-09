import PocketBase from 'pocketbase';

// Use environment variable or default to local instance
const url = import.meta.env.VITE_POCKETBASE_URL || 'https://pocketbase.thynaptic.com';
const pb = new PocketBase(url);

// Global real-time subscription helper could go here if needed
// but usually components handle their own subscriptions to specific collections.

export default pb;
