// import "isomorphic-fetch";

// first
Object.defineProperty(window, 'MutationObserver', { value: class {
    constructor(callback: any) {}
    disconnect() {}
    observe(element: any, initObject: any) {}
}});

import {main} from '../../src/ts/main';

// import * as puppeteer from"puppeteer";
// import * as path from "path";
describe('Checks browser interactions', () => {
    test("Check extension", () => {

    });
});


describe('Checks exports', () => {
    test("Check import", () => {
        console.log(main);
    });
});

