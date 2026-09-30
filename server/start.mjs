import { spawn } from 'node:child_process';
const children=[];
const run=(cmd,args)=>{const p=spawn(cmd,args,{stdio:'inherit',shell:process.platform==='win32'});children.push(p);return p};
run(process.execPath,['server/trace-api.mjs']);
run('npx',['vite']);
const stop=()=>{for(const p of children){try{p.kill('SIGTERM')}catch{}}};
process.on('SIGINT',()=>{stop();process.exit(0)});process.on('SIGTERM',()=>{stop();process.exit(0)});
