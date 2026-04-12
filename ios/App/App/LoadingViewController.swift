import UIKit
import Capacitor
import WebKit

class LoadingViewController: CAPBridgeViewController {

    private var loadingOverlay: UIView?
    private var progressView: UIProgressView?
    private var simulationTimer: Timer?

    override func viewDidLoad() {
        super.viewDidLoad()
        addLoadingOverlay()
        startProgressSimulation()
    }

    // MARK: - Overlay setup

    private func addLoadingOverlay() {
        let overlay = UIView(frame: view.bounds)
        overlay.autoresizingMask = [.flexibleWidth, .flexibleHeight]

        // Splash image — fills the overlay exactly like the launch screen
        let splash = UIImageView(image: UIImage(named: "Splash"))
        splash.contentMode = .scaleAspectFill
        splash.frame = overlay.bounds
        splash.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        overlay.addSubview(splash)

        // Progress bar
        let progress = UIProgressView(progressViewStyle: .default)
        progress.progressTintColor = UIColor(red: 212/255, green: 134/255, blue: 60/255, alpha: 1) // burnt orange #d4863c
        progress.trackTintColor  = UIColor(red: 30/255,  green: 58/255,  blue: 95/255,  alpha: 0.7) // #1e3a5f
        progress.layer.cornerRadius = 3
        progress.clipsToBounds = true
        // Make the bar a bit thicker
        progress.transform = CGAffineTransform(scaleX: 1, y: 2.5)
        progress.translatesAutoresizingMaskIntoConstraints = false
        overlay.addSubview(progress)
        NSLayoutConstraint.activate([
            progress.centerXAnchor.constraint(equalTo: overlay.centerXAnchor),
            progress.centerYAnchor.constraint(equalTo: overlay.centerYAnchor),
            progress.widthAnchor.constraint(equalTo: overlay.widthAnchor, multiplier: 0.55)
        ])

        view.addSubview(overlay)
        loadingOverlay = overlay
        progressView = progress
    }

    // MARK: - Progress simulation

    private func startProgressSimulation() {
        // Ramp quickly to ~80%, then wait for the real finish event
        simulationTimer = Timer.scheduledTimer(withTimeInterval: 0.06, repeats: true) { [weak self] timer in
            guard let self, let pv = self.progressView else { return }
            let next = min(pv.progress + Float.random(in: 0.015...0.045), 0.80)
            pv.setProgress(next, animated: true)
            if next >= 0.80 { timer.invalidate() }
        }
    }

    // MARK: - WebView delegate

    override func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        super.webView(webView, didFinish: navigation)
        simulationTimer?.invalidate()
        UIView.animate(withDuration: 0.25) {
            self.progressView?.setProgress(1.0, animated: true)
        } completion: { _ in
            UIView.animate(withDuration: 0.35, delay: 0.15) {
                self.loadingOverlay?.alpha = 0
            } completion: { _ in
                self.loadingOverlay?.removeFromSuperview()
                self.loadingOverlay = nil
            }
        }
    }
}
