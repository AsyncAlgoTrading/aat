/* eslint-disable @typescript-eslint/no-empty-function */
// import "isomorphic-fetch";

// first
Object.defineProperty(window, "MutationObserver", { value: class {
  public constructor(callback: any) {}
  public disconnect() {}
  public observe(element: any, initObject: any) {}
}});

import {main} from "../../src/ts/index";

// import * as puppeteer from"puppeteer";
// import * as path from "path";
describe("Checks browser interactions", () => {
  test("Check extension", () => {

  });
});


describe("Checks exports", () => {
  test("Check import", () => {
    // eslint-disable-next-line no-console
    console.log(main);
  });
});

