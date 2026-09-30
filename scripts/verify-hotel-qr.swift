import Foundation
import Vision
import AppKit
for path in CommandLine.arguments.dropFirst() {
 let request = VNDetectBarcodesRequest()
 request.symbologies = [.qr]
 try VNImageRequestHandler(url: URL(fileURLWithPath: path)).perform([request])
 let values = (request.results ?? []).compactMap { $0.payloadStringValue }
 precondition(values == ["https://getfluentfast.app/reading/vocab-reading-beff7eb59b8cf7ae5198a47a/"], "QR mismatch: \(path): \(values)")
 print("Decoded \(path): \(values[0])")
}
