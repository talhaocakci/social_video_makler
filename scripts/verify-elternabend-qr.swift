import Foundation
import Vision
import AppKit
for path in CommandLine.arguments.dropFirst() {
 let request = VNDetectBarcodesRequest()
 request.symbologies = [.qr]
 try VNImageRequestHandler(url: URL(fileURLWithPath: path)).perform([request])
 let values = (request.results ?? []).compactMap { $0.payloadStringValue }
 precondition(values == ["https://getfluentfast.app/reading/reading_elternabend_seed_de/"], "QR mismatch: \(path): \(values)")
 print("Decoded \(path): \(values[0])")
}
