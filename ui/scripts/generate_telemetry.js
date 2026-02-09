
import PocketBase from 'pocketbase';

// Configuration
const PB_URL = 'https://pocketbase.thynaptic.com'; // Adjust if needed
const COLLECTION = 'scac_system_health';
const INTERVAL_MS = 5000;

const pb = new PocketBase(PB_URL);

// Mock Nodes
const NODES = [
    { id: 'NODE-ALPHA-1', region: 'us-east-1', status: 'optimal' },
    { id: 'NODE-BETA-4', region: 'eu-west-2', status: 'optimal' },
    { id: 'NODE-GAMMA-9', region: 'ap-northeast-1', status: 'warning' },
    { id: 'NODE-DELTA-2', region: 'us-west-2', status: 'optimal' },
];

// Helper to generate random int
const randomInt = (min, max) => Math.floor(Math.random() * (max - min + 1) + min);

async function authenticate() {
    try {
        // Authenticate as admin to ensure we can write to the collection
        // In a real scenario, you'd use a dedicated bot account/token
        // For now, we'll try to use a preset email/pass or just anonymous if allow/create is open
        // But usually, admin is best for backend scripts. 
        // Let's assume public create access for now based on previous context, 
        // or attempt a standard login if provided.
        // Actually, let's try to just write. If it fails, we'll log it.
        // NOTE: You might need to disable API rules or login.

        console.log(`Connecting to ${PB_URL}...`);

        // Attempt to login with a fallback admin if environment variables exist, 
        // otherwise proceed (assuming open permissions for this demo)
        if (process.env.PB_ADMIN_EMAIL && process.env.PB_ADMIN_PASS) {
            await pb.admins.authWithPassword(process.env.PB_ADMIN_EMAIL, process.env.PB_ADMIN_PASS);
            console.log('Authenticated as Admin');
        }
    } catch (err) {
        console.error('Authentication failed (proceeding as guest):', err.message);
    }
}

async function updateTelemetry() {
    console.log(`\n[${new Date().toISOString()}] Generating Telemetry...`);

    for (const node of NODES) {
        // Stimulate values
        // CPU: 10-50% for optimal, 70-95% for warning
        // Mem: similar
        let cpu, memory;

        if (node.status === 'warning') {
            cpu = randomInt(70, 98);
            memory = randomInt(60, 95);
        } else {
            cpu = randomInt(10, 60);
            memory = randomInt(20, 60);
        }

        // Randomly flip status occasionally
        if (Math.random() > 0.9) {
            node.status = node.status === 'optimal' ? 'warning' : 'optimal';
        }

        const data = {
            node_id: node.id,
            region: node.region,
            status: node.status,
            cpu_usage: cpu,
            memory_usage: memory,
            uptime: '14d 2h 12m', // Static for now, or could parse start time
            network_latency: randomInt(10, 150)
        };

        try {
            // Check if record exists for this node
            const records = await pb.collection(COLLECTION).getList(1, 1, {
                filter: `node_id = "${node.id}"`
            });

            if (records.items.length > 0) {
                // Update
                await pb.collection(COLLECTION).update(records.items[0].id, data);
                console.log(`Updated ${node.id}: CPU=${cpu}%, MEM=${memory}%`);
            } else {
                // Create
                await pb.collection(COLLECTION).create(data);
                console.log(`Created ${node.id}: CPU=${cpu}%, MEM=${memory}%`);
            }
        } catch (error) {
            if (error.status === 404) {
                console.error(`Collection '${COLLECTION}' not found. Please create it in PocketBase.`);
            } else {
                console.error(`Error processing ${node.id}:`, error);
                console.error('Payload:', JSON.stringify(data, null, 2));
            }
        }
    }
}

async function main() {
    await authenticate();

    // Initial run
    await updateTelemetry();

    // Loop
    setInterval(updateTelemetry, INTERVAL_MS);
}

main();
