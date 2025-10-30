export * from "./backend";

export function promiseWithResolver<T>(): [Promise<T>, (value: T) => void, (error: any) => void] {
    let resolve: (object: T) => void;
    let reject: (error: any) => void;
    const promise = new Promise<T>((res, rej) => (resolve = res, reject = rej));

    return [promise, resolve!, reject!];
}
